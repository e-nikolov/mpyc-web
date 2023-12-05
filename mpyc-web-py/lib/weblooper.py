import asyncio
import collections
import contextvars
import logging
from typing import Any, Callable, Optional

import js
from pyodide import webloop
from pyodide.code import run_js
from pyodide.ffi import IN_BROWSER, create_once_callable, create_proxy

run_js("""    
    self.webChannel = new MessageChannel()
""")

setTimeout = js.setTimeout
# webloop.setTimeout = js.webloopSetTimeout
chan = js.webChannel


class WebLooper(webloop.WebLoop):
    def __init__(self):
        super().__init__()

        self._ready = collections.deque()
        self._callbacks = {}
        self.counter = 0
        self.call_immediate_count = 0
        self.call_later_count = 0
        self.call_callback_count = 0
        self.queue = collections.deque()
        # self.call_proxy = create_proxy(self.call_callback)

        chan.port1.onmessage = self.call_callback

        # self._callbacks[id] = run_handle

        # chan.port1.onmessage =

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
            self.queue.appendleft(run_handle)
            # print("posting message", self.queue)
            chan.port2.postMessage("")
            self.call_immediate_count += 1
            return h

        # self._ready.append(h)
        self.call_later_count += 1
        setTimeout(create_once_callable(run_handle), delay * 1000)
        return h

    # @stats.acc(lambda self, *args, **kwargs: {"$func": "calls"})
    def call_callback(self, *args, **kwargs):
        # print("call_callback")
        self.queue.pop()()

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
