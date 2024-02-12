# pyright: ignore

"""
This module provides a `StatsCollector` class that can be used to collect and print statistics about various events
in the program. The `StatsCollector` class is a subclass of `BaseStatsCollector`, which provides the core functionality
for collecting and updating statistics.

The `StatsCollector` class defines several methods that can be used to collect statistics for different types of events,
such as `total_calls`, `sent_to`, and `received_from`. These methods return dictionaries that can be passed to the
`update` method of a `DeepCounter` object to update the statistics.

The `DeepCounter` class is a subclass of `dict` that provides a way to update nested dictionaries with numeric values.
It defines the `update` and `set` methods, which can be used to update or set the values of nested dictionaries.

The `BaseStatsCollector` class defines a decorator `dec` that can be used to decorate functions and collect statistics
about their calls. The `acc` method of `BaseStatsCollector` returns a decorator that can be used to collect statistics
about the arguments passed to a function.
"""

import asyncio
import gc
import io
import json
import logging
import math
import time
from collections import deque
from contextlib import ContextDecorator
from datetime import datetime
from functools import wraps
from re import L
from typing import Callable, ParamSpec, TypeVar

import humanize
import rich
import yaml
from humanize import naturalsize
from lib import log_levels
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from .rstats.rstats import BaseStatsCollector  # , format_time
from .rstats.rstats import BaseStatsState, MovingAverage, NestedDict, TimeStats, format_count, format_file_size

# type: ignore-all
logger = logging.getLogger(__name__)


# pyright: ignore-all
# pylint: disable=all
# pyright: ignore=all
# type: ignore=all


class AsyncioStats:
    tasks = 0
    max_tasks = 0
    loop_iters = 0
    loop_reiters = 0
    loop_inner_iters = 0
    ready = 0
    total_tasks_count = 0
    eager_tasks_count = 0
    total_eager_tasks_count = 0
    total_scheduled_tasks_count = 0
    scheduled_tasks_count = 0
    call_soon_count = 0
    call_later_count = 0
    ntodo = 0

    def __str__(self):
        return (
            f"tasks: ce {format_count(self.eager_tasks_count)} / cs {format_count(self.scheduled_tasks_count)} / c {format_count(self.tasks)} / ∨ {format_count(self.max_tasks)} / ∑"
            f" {format_count(self.total_tasks_count)} ({format_count(self.total_eager_tasks_count)} + {format_count(self.total_scheduled_tasks_count)}) | loop: o {format_count(self.loop_iters)} / i"
            f" {format_count(self.loop_inner_iters)} / {format_count(self.ntodo)}"
        )


class DataStats:
    initialized = False

    sent = 0
    received = 0

    def __str__(self):
        if not self.initialized:
            return ""
        return f"⬆{format_file_size(self.sent)} / ⬇{format_file_size(self.received)}"


class MessageStats:
    initialized = False

    sent = 0
    received = 0

    def __str__(self):
        if not self.initialized:
            return ""

        return f"⬆{format_count(self.sent)} / ⬇{format_count(self.received)}"


# def format_asyncio_stats(stats: AsyncioStats):
#     return (
#             f"tasks: ce {format_count(stats.eager_tasks_count)} / cs {format_count(stats.scheduled_tasks_count)} / c {format_count(stats.tasks)} / ∨ {format_count(stats.max_tasks)} / ∑"
#             f" {format_count(stats.total_tasks_count)} ({format_count(stats.total_eager_tasks_count)} + {format_count(stats.total_scheduled_tasks_count)}) | loop: o {format_count(stats.loop_iters)} / i"
#             f" {format_count(stats.loop_inner_iters)} / {format_count(stats.ntodo)}"
#         )


# def format_data(data):
#     sent, received = 0, 0
#     if "sent" in data:
#         sent = data["sent"]

#     if "received" in data:
#         received = data["received"]

#     return f"⬆{format_file_size(sent)} / ⬇{format_file_size(received)}"


# def format_messages(messages):
#     sent, received = 0, 0
#     if "sent" in messages:
#         sent = messages["sent"]

#     if "received" in messages:
#         received = messages["received"]

#     return f"⬆{format_count(sent)} / ⬇{format_count(received)}"


class StatsState(BaseStatsState):
    def __init__(self):
        super().__init__()

        self.asyncio = AsyncioStats()
        self.gc = {}
        self.latency = TimeStats()
        self.data = DataStats()
        self.messages = MessageStats()


class StatsCollector(BaseStatsCollector):
    """
    A class for collecting statistics on messages sent and received by MPC parties.

    Attributes:
        None

    Methods:
        stat(s: NestedDict[str, float]) -> NestedDict[str, float]: Returns the input dictionary unchanged.
        total_calls() -> NestedDict[str, float]: Returns a dictionary with a single key-value pair indicating a function call was made.
        sent_to(pid: int, msg: bytes) -> NestedDict[str, float]: Returns a dictionary with statistics on a message sent to a specific MPC party.
        received_from(pid: int, msg: bytes) -> NestedDict[str, float]: Returns a dictionary with statistics on a message received from a specific MPC party.
    """

    def __init__(self):
        state = StatsState()

        super().__init__(
            formatters={
                # "messages": format_messages,
                # "asyncio": format_asyncio_stats,
                # "data": format_data,
                # "latency": format_time,
            },
            on_before_get_stats_hooks=[self.asyncio_stats, self.gc_stats],
            state=state,
        )

        self.state = state

    def asyncio_stats(self, stats: BaseStatsCollector, label="asyncio"):
        # if label not in stats.stats.counter:
        #     return

        tasks = len(asyncio.tasks._eager_tasks) + len(asyncio.tasks._scheduled_tasks)
        if tasks > self.state.asyncio.max_tasks:
            self.state.asyncio.max_tasks = tasks

        self.state.asyncio.tasks = tasks

        stats.state.__dict__[label] = self.state.asyncio

    def gc_stats(self, stats: BaseStatsCollector, label="gc"):
        if not logger.isEnabledFor(5):
            return

        stats[label] = gc.get_stats()

    def reset(self):
        state = StatsState()
        super().reset(state=state)
        self.state = state

    def latency(self, ts: float):  # pyright: ignore
        if not self.enabled:
            return

        self.state.latency.initialized = True

        l = time.time_ns() // 1000 - ts
        if l <= 0:
            return
        self.state.latency.update(l)

    def add(self, path=["default"], value=1):  # pyright: ignore
        if not self.enabled:
            return

        self.state.__dict__.acc_path(value, *path)

    def sent_to(self, pid: int, msg: bytes) -> NestedDict[str, float]:
        if not self.enabled:
            return

        self.state.messages.initialized = True
        self.state.data.initialized = True

        self.state.messages.sent += 1
        self.state.data.sent += len(msg)
        # f"messages_sent_to[{pid}]": +1,
        # f"bytes_sent_to[{pid}]": +len(msg),

    def received_from(self, pid: int, msg: bytes) -> NestedDict[str, float]:
        if not self.enabled:
            return

        self.state.messages.initialized = True
        self.state.data.initialized = True

        self.state.messages.received += 1
        self.state.data.received += len(msg)
        # f"messages_received_from[{pid}]": +1,
        # f"bytes_received_from[{pid}]": +len(msg),


# class BaseDecorator[**P, R](ContextDecorator):
#     def __init__(self, stats: BaseStatsCollector[P, R], label="default"):
#         self.stats = stats
#         self.label = label

#     def decorator(func: Callable[P, R]) -> Callable[P, R]:
#         @wraps(func)
#         def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
#             if not self.enabled:
#                 return func(*args, **kwargs)
#             new_stats: NestedDict[str, Numeric] = make_stats_func(*args, **kwargs)
#             res = func(*args, **kwargs)
#             if FUNC_ARG in new_stats:
#                 f_name = func.__name__
#                 func_stats = new_stats.pop(FUNC_ARG)
#                 new_stats |= {f_name: func_stats}

#                 if f_name not in self.stats:  # pyright: ignore
#                     self.stats[f_name] = {}  # pyright: ignore

#             update_func()(new_stats)
#             return res

#         return wrapper

#         return decorator


DEFAULT_LABEL = "default"


class BaseContext[**P, R](ContextDecorator):

    def __init__(self, stats: StatsCollector, make_new_stats_func: Callable[P, R], label="default"):
        self.stats = stats
        self.timings = None
        self.label = label
        self.make_new_stats_func = make_new_stats_func
        self.new_stats = None
        self.args = None
        self.kwargs = None

    def __call__(self, func, *args, **kwargs):  # only called when used as a decorator
        print("__call__", func, args, kwargs)
        self.func = func
        if self.label is DEFAULT_LABEL:
            self.label = func.__name__
        return super().__call__(func)

    def __enter__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        print("__enter__", args, kwargs)
        if not self.stats.enabled:
            return

        if self.label is DEFAULT_LABEL:
            f = sys._getframe().f_back
            if f is not None:
                f_name, line = f.f_code.co_name, f.f_lineno
                self.label = f"{f_name}:{line}"

        # new_stats = self.make_new_stats_func(self.args, self.kwargs)
        print(self.make_new_stats_func, *self.args, **self.kwargs)
        self.make_new_stats_func(self.args, self.kwargs)
        # self.stats[self.label] = new_stats

        # self.start_time = time.perf_counter_ns()

    def __exit__(self, *args):
        if not self.stats.enabled:
            return

        # self.stats._update_timings(self.label, (time.perf_counter_ns() - self.start_time) // 1000)


stats = StatsCollector()
