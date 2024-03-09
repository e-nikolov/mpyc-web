import asyncio
import collections
import contextvars
import types
from asyncio import tasks
from functools import partial, partialmethod
from random import sample, shuffle
from typing import Any, Callable, Optional

import js
import rich
from lib.api import async_proxy
from lib.stats import MovingAverage, stats
from pyodide.code import run_js
from pyodide.ffi import IN_BROWSER, create_once_callable, create_proxy
from pyodide.webloop import PyodideFuture, PyodideTask, WebLoop

scheduleCallback = run_js(
    """
const channel = new MessageChannel();

self.queue = {};
self.readyCounter = 0;
self.doneCounter = 0;

let running = false;

_runOnce = () => {
    self.ntodo = self.readyCounter - self.doneCounter;
    while(self.doneCounter < self.readyCounter) {
        self.doneCounter++;
        queue[self.doneCounter]();
        delete queue[self.doneCounter];
    }
    running = false
};

channel.port1.onmessage = (_) => _runOnce()

function runOnce() {
    channel.port2.postMessage(undefined);
}

function scheduleCallback(callback, timeout) {
    if (timeout >= 4) {
        return setTimeout(callback, timeout);
    }
    
    queue[++self.readyCounter] = callback;
    if(!running) {
        running = true
        runOnce()
    }
}

scheduleCallback
"""
)


class WebLooper(WebLoop):
    def __init__(self):
        super().__init__()
        stats.reset()

    def run_handle(self, h: asyncio.Handle):
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

    def call_soon(
        self,
        callback: Callable[..., Any],
        *args: Any,
        context: contextvars.Context | None = None,
    ) -> asyncio.Handle:
        h = asyncio.Handle(callback, args, self, context=context)
        scheduleCallback(create_once_callable(h._run), 0)
        return h

    def call_later(  # type: ignore[override]
        self,
        delay: float,
        callback: Callable[..., Any],
        *args: Any,
        context: contextvars.Context | None = None,
    ) -> asyncio.Handle:
        h = asyncio.Handle(callback, args, self, context=context)

        scheduleCallback(create_once_callable(h._run), delay * 1000)

        return h

    def create_task(self, coro, *, name=None):
        """Schedule a coroutine object.

        Return a task object.

        Copied from ``BaseEventLoop.create_task``
        """
        self._check_closed()
        if self._task_factory is None:
            task = PyodideTaskStats(coro, loop=self, name=name)
            if task._source_traceback:  # type: ignore[attr-defined]
                # Added comment:
                # this only happens if get_debug() returns True.
                # In that case, remove create_task from _source_traceback.
                del task._source_traceback[-1]  # type: ignore[attr-defined]
        else:
            task = self._task_factory(self, coro)
            tasks._set_task_name(task, name)  # type: ignore[attr-defined]

        self._in_progress += 1
        task.add_done_callback(self._decrement_in_progress)
        return task


class PyodideTaskStats(PyodideTask):
    def __init__(self, coro, *, loop=None, name=None, context=None, eager_start=True):
        super().__init__(coro, loop=loop, name=name, eager_start=eager_start)
        stats.state.asyncio.total_tasks_count += 1

        if eager_start:
            stats.state.asyncio.total_eager_tasks_count += 1
        else:
            stats.state.asyncio.total_scheduled_tasks_count += 1
