import asyncio
import collections
import contextvars
import types
from typing import Any, Callable, Optional

import js
from pyodide.code import run_js
from pyodide.ffi import IN_BROWSER, create_once_callable, create_proxy
from pyodide.webloop import PyodideFuture, PyodideTask, WebLoop

run_js("""    
    self.webChannel = new MessageChannel()
""")

setTimeout = js.setTimeout
# webloop.setTimeout = js.webloopSetTimeout
chan = js.webChannel


class WebLooper(WebLoop):
    def __init__(self):
        super().__init__()

        loop = self
        old_add = asyncio.tasks._all_tasks.add

        def add(self, task):
            loop.total_tasks_count += 1
            old_add(task)

        asyncio.tasks._all_tasks.add = types.MethodType(add, asyncio.tasks._all_tasks)

        self.loop_iters = 0
        self._ready = collections.deque()
        self._callbacks = {}
        self.counter = 0
        self.total_tasks_count = len(asyncio.tasks._all_tasks)
        self.total_futures_count = 0
        self.call_soon_count = 0
        self.call_later_count = 0
        self.call_callback_count = 0
        self._run_once_proxy = create_proxy(self._run_once)
        # self.call_proxy = create_proxy(self.call_callback)

        # js.setTimeout(self._run_once_proxy, 0)
        chan.port1.onmessage = create_proxy(self.call_callback)

        chan.port2.postMessage(None)

        # self._callbacks[id] = run_handle

        # chan.port1.onmessage =

    def _run_forever(self):
        while True:
            self._run_once()

    def _run_once(self):
        self.loop_iters += 1

        ntodo = len(self._ready)
        for i in range(ntodo):
            self._ready.popleft()()

        # js.setTimeout(self._run_once_proxy, 0)
        chan.port2.postMessage(None)

    # @stats.acc(lambda self, callb)
    def call_soon(
        self,
        callback: Callable[..., Any],
        *args: Any,
        context: contextvars.Context | None = None,
    ) -> asyncio.Handle:
        """Arrange for a callback to be called as soon as possible.

        Any positional arguments after the callback will be passed to
        the callback when it is called.

        This schedules the callback on the browser event loop using ``setTimeout(callback, 0)``.
        """
        delay = 0
        return self.call_later(delay, callback, *args, context=context)

    def call_later(  # type: ignore[override]
        self,
        delay: float,
        callback: Callable[..., Any],
        *args: Any,
        context: contextvars.Context | None = None,
    ) -> asyncio.Handle:
        """Arrange for a callback to be called at a given time.

        Return a Handle: an opaque object with a cancel() method that
        can be used to cancel the call.

        The delay can be an int or float, expressed in seconds.  It is
        always relative to the current time.

        Each callback will be called exactly once.  If two callbacks
        are scheduled for exactly the same time, it undefined which
        will be called first.

        Any positional arguments after the callback will be passed to
        the callback when it is called.

        This uses `setTimeout(callback, delay)`
        """
        # print("call_later", delay, callback, args)
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
            self._ready.append(run_handle)
            self.call_soon_count += 1

            return h

        # self._ready.append(h)
        self.call_later_count += 1
        # print("call_later", delay, callback, args, f"{self.call_later_count=}")
        setTimeout(create_once_callable(run_handle), delay * 1000)
        return h

    # @stats.acc(lambda self, *args, **kwargs: {"$func": "calls"})
    def call_callback(self, *args, **kwargs):
        # print("call_callback")
        # self._ready.popleft()()
        self._run_once()

    def _decrement_in_progress(self, *args):
        # print("_decrement_in_progress", args)
        self._in_progress -= 1
        if self._no_in_progress_handler and self._in_progress == 0:
            self._no_in_progress_handler()

    def create_future(self) -> asyncio.Future[Any]:
        self._in_progress += 1
        self.total_futures_count += 1
        fut: PyodideFuture[Any] = PyodideFuture(loop=self)
        fut.add_done_callback(self._decrement_in_progress)
        """Create a Future object attached to the loop."""
        return fut

    def create_task(self, coro, *, name=None):
        """Schedule a coroutine object.

        Return a task object.

        Copied from ``BaseEventLoop.create_task``
        """
        self._check_closed()
        if self._task_factory is None:
            task = PyodideTask(coro, loop=self, name=name)
            if task._source_traceback:  # type: ignore[attr-defined]
                # Added comment:
                # this only happens if get_debug() returns True.
                # In that case, remove create_task from _source_traceback.
                del task._source_traceback[-1]  # type: ignore[attr-defined]
        else:
            task = self._task_factory(self, coro)
            asyncio.tasks._set_task_name(task, name)  # type: ignore[attr-defined]

        self._in_progress += 1
        # self.total_tasks_count += 1
        task.add_done_callback(self._decrement_in_progress)
        return task

    # def _do_tasks(
    #     self,
    #     until_complete: Optional[bool] = False,
    #     forever: Optional[bool] = False,
    # ):
    #     """
    #     Do the tasks
    #     """
    #     self._exception = None
    #     self._result = None
    #     self._running = True
    #     if self._stop:
    #         self._quit_running()
    #         return
    #     while len(self._immediate) > 0:
    #         h = self._immediate[0]
    #         self._immediate = self._immediate[1:]
    #         if not h._cancelled:
    #             h._run()
    #         if self._stop:
    #             self._quit_running()
    #             return

    #     if self._next_handle is not None:
    #         if self._next_handle._cancelled:
    #             self._next_handle = None

    #     if self._scheduled and self._next_handle is None:
    #         h = heapq.heappop(self._scheduled)
    #         h._scheduled = True
    #         self._next_handle = h

    #     if self._next_handle is not None and self._next_handle._when <= self.time():
    #         h = self._next_handle
    #         self._next_handle = None
    #         self._immediate.append(h)

    #     not_finished = self._immediate or self._scheduled or self._next_handle or self._futures
    #     if forever or (until_complete and not_finished):
    #         self._timeout_promise(self._interval).then(lambda x: self._do_tasks(until_complete=until_complete, forever=forever))
    #     else:
    #         self._quit_running()

    # def _run_once(self):
    #     """Run one full iteration of the event loop.

    #     This calls all currently ready callbacks, polls for I/O,
    #     schedules the resulting callbacks, and finally schedules
    #     'call_later' callbacks.
    #     """

    #     sched_count = len(self._scheduled)
    #     if sched_count > _MIN_SCHEDULED_TIMER_HANDLES and self._timer_cancelled_count / sched_count > _MIN_CANCELLED_TIMER_HANDLES_FRACTION:
    #         # Remove delayed calls that were cancelled if their number
    #         # is too high
    #         new_scheduled = []
    #         for handle in self._scheduled:
    #             if handle._cancelled:
    #                 handle._scheduled = False
    #             else:
    #                 new_scheduled.append(handle)

    #         heapq.heapify(new_scheduled)
    #         self._scheduled = new_scheduled
    #         self._timer_cancelled_count = 0
    #     else:
    #         # Remove delayed calls that were cancelled from head of queue.
    #         while self._scheduled and self._scheduled[0]._cancelled:
    #             self._timer_cancelled_count -= 1
    #             handle = heapq.heappop(self._scheduled)
    #             handle._scheduled = False

    #     timeout = None
    #     if self._ready or self._stopping:
    #         timeout = 0
    #     elif self._scheduled:
    #         # Compute the desired timeout.
    #         timeout = self._scheduled[0]._when - self.time()
    #         if timeout > MAXIMUM_SELECT_TIMEOUT:
    #             timeout = MAXIMUM_SELECT_TIMEOUT
    #         elif timeout < 0:
    #             timeout = 0

    #     event_list = self._selector.select(timeout)
    #     self._process_events(event_list)
    #     # Needed to break cycles when an exception occurs.
    #     event_list = None

    #     # Handle 'later' callbacks that are ready.
    #     end_time = self.time() + self._clock_resolution
    #     while self._scheduled:
    #         handle = self._scheduled[0]
    #         if handle._when >= end_time:
    #             break
    #         handle = heapq.heappop(self._scheduled)
    #         handle._scheduled = False
    #         self._ready.append(handle)

    #     # This is the only place where callbacks are actually *called*.
    #     # All other places just add them to ready.
    #     # Note: We run all currently scheduled callbacks, but not any
    #     # callbacks scheduled by callbacks run this time around --
    #     # they will be run the next time (after another I/O poll).
    #     # Use an idiom that is thread-safe without using locks.
    #     ntodo = len(self._ready)
    #     for i in range(ntodo):
    #         handle = self._ready.popleft()
    #         if handle._cancelled:
    #             continue
    #         if self._debug:
    #             try:
    #                 self._current_handle = handle
    #                 t0 = self.time()
    #                 handle._run()
    #                 dt = self.time() - t0
    #                 if dt >= self.slow_callback_duration:
    #                     logger.warning("Executing %s took %.3f seconds", _format_handle(handle), dt)
    #             finally:
    #                 self._current_handle = None
    #         else:
    #             handle._run()
    #     handle = None  # Needed to break cycles when an exception occurs.
