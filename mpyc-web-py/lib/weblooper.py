import asyncio
import collections
import contextvars
import types
from typing import Any, Callable, Optional

import js
from pyodide.code import run_js
from pyodide.ffi import IN_BROWSER, create_once_callable, create_proxy
from pyodide.webloop import PyodideFuture, PyodideTask, WebLoop


class WebLooper(WebLoop):
    def __init__(self):
        super().__init__()

        loop = self
        old_add = asyncio.tasks._all_tasks.add

        def add(self, task):
            loop.total_tasks_count += 1
            old_add(task)

        asyncio.tasks._all_tasks.add = types.MethodType(add, asyncio.tasks._all_tasks)

        self.running = False
        self.loop_iters = 0
        self._ready = collections.deque()
        self._callbacks = {}
        self.counter = 0
        self.total_tasks_count = len(asyncio.tasks._all_tasks)
        self.total_futures_count = 0
        self.call_soon_count = 0
        self.call_later_count = 0
        self.call_callback_count = 0
        self.promise = js.Promise.resolve()
        self._run_once_proxy = create_proxy(self._run_once)
        self.test_proxy = create_proxy(self._test)

    def _test(self, *args):
        js.console.warn("test????????????????????????????????????")
        print("test????????????????????????????????????")

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
            if h.cancelled():
                return
            try:
                # print("running handle", self.counter)
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
            self.call_soon_count += 1
            self._ready.append(run_handle)
            if not self.running:
                self.running = True
                # js.console.warn("call_later")
                # js.console.warn("call_later")
                # self.promise.then(self.test_proxy)
                # self.promise.then(self.test_proxy)
                # js.console.warn("call_later")
                # self.promise.then(self._run_once_proxy)
                self._run_once_proxy()
                # js.queueMicrotask(self._run_once_proxy)

            return h

        # self._ready.append(h)
        self.call_later_count += 1
        # print("call_later", delay, callback, args, f"{self.call_later_count=}")
        js.setTimeout(create_once_callable(run_handle), delay * 1000)
        return h

    def _run_once(self, *args, **kwargs):
        js.console.warn("_run_once")
        self.loop_iters += 1

        while len(self._ready) > 0:
            self._ready.popleft()()

        self.running = False
