import asyncio
import collections
import contextvars
import types
from asyncio import Future, tasks
from functools import partial, partialmethod
from random import sample, shuffle
from typing import Any, Awaitable, Callable, Optional, TypeVar, overload

import js
import rich
from lib.api import async_proxy
from lib.stats import MovingAverage, stats
from pyodide.code import run_js
from pyodide.ffi import IN_BROWSER, create_once_callable, create_proxy
from pyodide.webloop import PyodideTask, WebLoop

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
    
    queueMicrotask(callback);
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


T = TypeVar("T")
S = TypeVar("S")


class PyodideFuture(Future[T]):
    """A :py:class:`~asyncio.Future` with extra :js:meth:`~Promise.then`,
    :js:meth:`~Promise.catch`, and :js:meth:`finally_() <Promise.finally>` methods
    based on the Javascript promise API. :py:meth:`~asyncio.loop.create_future`
    returns these so in practice all futures encountered in Pyodide should be an
    instance of :py:class:`~pyodide.webloop.PyodideFuture`.
    """

    @overload
    def then(
        self,
        onfulfilled: None,
        onrejected: Callable[[BaseException], Awaitable[S]],
    ) -> "PyodideFuture[S]": ...

    @overload
    def then(
        self,
        onfulfilled: None,
        onrejected: Callable[[BaseException], S],
    ) -> "PyodideFuture[S]": ...

    @overload
    def then(
        self,
        onfulfilled: Callable[[T], Awaitable[S]],
        onrejected: Callable[[BaseException], Awaitable[S]] | None = None,
    ) -> "PyodideFuture[S]": ...

    @overload
    def then(
        self,
        onfulfilled: Callable[[T], S],
        onrejected: Callable[[BaseException], S] | None = None,
    ) -> "PyodideFuture[S]": ...

    def then(
        self,
        onfulfilled: Callable[[T], S | Awaitable[S]] | None,
        onrejected: Callable[[BaseException], S | Awaitable[S]] | None = None,
    ) -> "PyodideFuture[S]":
        """When the Future is done, either execute onfulfilled with the result
        or execute onrejected with the exception.

        Returns a new Future which will be marked done when either the
        onfulfilled or onrejected callback is completed. If the return value of
        the executed callback is awaitable it will be awaited repeatedly until a
        nonawaitable value is received. The returned Future will be resolved
        with that value. If an error is raised, the returned Future will be
        rejected with the error.

        Parameters
        ----------
        onfulfilled:
            A function called if the Future is fulfilled. This function receives
            one argument, the fulfillment value.

        onrejected:
            A function called if the Future is rejected. This function receives
            one argument, the rejection value.

        Returns
        -------
            A new future to be resolved when the original future is done and the
            appropriate callback is also done.
        """
        print("PyodideFuture then")

        result: PyodideFuture[S] = PyodideFuture()

        onfulfilled_: Callable[[T], S | Awaitable[S]]
        onrejected_: Callable[[BaseException], S | Awaitable[S]]
        if onfulfilled:
            onfulfilled_ = onfulfilled
        else:

            def onfulfilled_(x):
                return x

        if onrejected:
            onrejected_ = onrejected
        else:

            def onrejected_(x):
                raise x

        async def callback(fut: Future[T]) -> None:
            e = fut.exception()
            try:
                if e:
                    r = onrejected_(e)
                else:
                    r = onfulfilled_(fut.result())
                while inspect.isawaitable(r):
                    r = await r
            except Exception as result_exception:
                result.set_exception(result_exception)
                return
            result.set_result(r)

        def wrapper(fut: Future[T]) -> None:
            asyncio.ensure_future(callback(fut))

        self.add_done_callback(wrapper)
        return result

    @overload
    def catch(self, onrejected: Callable[[BaseException], Awaitable[S]]) -> "PyodideFuture[S]": ...

    @overload
    def catch(self, onrejected: Callable[[BaseException], S]) -> "PyodideFuture[S]": ...

    def catch(self, onrejected: Callable[[BaseException], object]) -> "PyodideFuture[Any]":
        """Equivalent to ``then(None, onrejected)``"""
        print("PyodideFuture catch")
        return self.then(None, onrejected)

    def finally_(self, onfinally: Callable[[], None]) -> "PyodideFuture[T]":
        """When the future is either resolved or rejected, call ``onfinally`` with
        no arguments.
        """
        print("PyodideFuture finally")
        result: PyodideFuture[T] = PyodideFuture()

        async def callback(fut: Future[T]) -> None:
            exc = fut.exception()
            try:
                r = onfinally()
                while inspect.isawaitable(r):
                    r = await r
            except Exception as e:
                result.set_exception(e)
                return
            if exc:
                result.set_exception(exc)
            else:
                result.set_result(fut.result())

        def wrapper(fut: Future[T]) -> None:
            asyncio.ensure_future(callback(fut))

        self.add_done_callback(wrapper)
        return result


class PyodideTaskStats(PyodideTask):
    def __init__(self, coro, *, loop=None, name=None, context=None, eager_start=True):
        print("PyodideTask init", coro)
        super().__init__(coro, loop=loop, name=name, eager_start=eager_start)
        # stats.state.asyncio.total_tasks_count += 1

        # if eager_start:
        #     stats.state.asyncio.total_eager_tasks_count += 1
        # else:
        #     stats.state.asyncio.total_scheduled_tasks_count += 1
