import asyncio
import collections
import contextvars
import types
from random import sample, shuffle
from typing import Any, Callable, Optional

import js
import rich
from lib.api import async_proxy
from lib.stats import MovingAverage, stats
from pyodide.code import run_js
from pyodide.ffi import IN_BROWSER, create_once_callable, create_proxy
from pyodide.webloop import PyodideFuture, PyodideTask, WebLoop


class WebLooper(WebLoop):
    def __init__(self):
        super().__init__()
        stats.reset()
        old_add = asyncio.tasks._all_tasks.add

        def add(self, task):
            stats_add("total_tasks_count")
            old_add(task)

        asyncio.tasks._all_tasks.add = types.MethodType(add, asyncio.tasks._all_tasks)
        stats_set("total_tasks_count", len(asyncio.tasks._all_tasks))

        self.running = False
        self._ready = collections.deque()
        self._run_once_proxy = create_proxy(self._run_once)
        self.chan = js.MessageChannel.new()
        self.chan.port1.onmessage = self._run_once_proxy

    def call_soon(
        self,
        callback: Callable[..., Any],
        *args: Any,
        context: contextvars.Context | None = None,
    ) -> asyncio.Handle:
        delay = 0
        return self.call_later(delay, callback, *args, context=context)

    def call_later(  # type: ignore[override]
        self,
        delay: float,
        callback: Callable[..., Any],
        *args: Any,
        context: contextvars.Context | None = None,
    ) -> asyncio.Handle:
        if delay < 0:
            raise ValueError("Can't schedule in the past")
        h = asyncio.Handle(callback, args, self, context=context)

        def run_handle():
            if h._cancelled:
                return
            try:
                h._run()
            except SystemExit as e:
                if self._system_exit_handler:
                    self._system_exit_handler(e.code)
                else:
                    raise
            except KeyboardInterrupt:
                if self._keyboard_interrupt_handler:
                    self._keyboard_interrupt_handler()
                else:
                    raise

        if delay == 0:
            stats_add("call_soon_count")
            self._ready.append(run_handle)
            if not self.running:
                self.running = True
                self.trigger_run_once()

            return h
        js.setTimeout(create_once_callable(run_handle), delay * 1000)
        return h

    def trigger_run_once(self):
        stats_add("loop_iters")
        self.chan.port2.postMessage(None)

    @stats.acc(lambda *args, **kwargs: stats.time())
    def _run_once(self, *args, **kwargs):
        ntodo = len(self._ready)
        stats_set("ntodo", ntodo)
        ntodoz(ntodo)
        async_proxy.maybe_send_stats()

        # sample_indices = set(sample(range(ntodo), ntodo))

        # ready_shuff = [self._ready[i] for i in sample_indices]
        # self._ready.clear()

        # for h in ready_shuff:
        #     stats_add("loop_inner_iters")
        #     h()

        while self._ready:
            stats_add("loop_inner_iters")
            self._ready.popleft()()

        nleft = len(self._ready)
        ntodoz(nleft, "left")
        if nleft == 0:
            self.running = False
        else:
            self.trigger_run_once()


def ntodoz(ntodo, key="ready"):
    if key not in stats.stats:
        stats.stats[key] = {  # pyright: ignore
            "min_cnt": 0,
            "max": 0,
            "avg": MovingAverage(maxlen=200),
        }
    stats.stats[key]["avg"].append(ntodo)
    if ntodo <= 0:
        stats.stats[key]["min_cnt"] += 1

    stats.stats[key]["max"] = max(ntodo, stats.stats[key]["max"]) if stats.stats[key]["max"] else ntodo  # pyright: ignore


def stats_add(path: str, value=1, prefix="asyncio."):
    stats.acc_path(f"{prefix}{path}", value)


def stats_set(path: str, value=1, prefix="asyncio."):
    stats.set_path(f"{prefix}{path}", value)
