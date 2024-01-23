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
import time
from collections import deque
from datetime import datetime
from functools import wraps
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

from .rstats.rstats import BaseStatsCollector, MovingAverage, format_count, format_file_size, format_time

# type: ignore-all
logger = logging.getLogger(__name__)

K = TypeVar("K")
V = TypeVar("V")
NestedDict = dict[K, V | "NestedDict[K, V]"]

Numeric = int | float

N = TypeVar("N", int, float)

# pyright: ignore-all
# pylint: disable=all
# pyright: ignore=all
# type: ignore=all


P = ParamSpec("P")
R = TypeVar("R")
import math


def format_asyncio_stats(stats):
    return (
        f't: {format_count(stats["tasks"])} / {format_count(stats["max_tasks"])} / {format_count(stats["total_tasks_count"])} \n'
        f' | l: {format_count(stats["call_soon_count"])}'
        f' / {format_count(stats["loop_inner_iters"])}'
        f' / {format_count(stats["loop_iters"])}'
        f' / {format_count(stats["loop_reiters"])} \n'
        f' | q: {format_count(stats["ready"])} / {format_count(stats["ntodo"])}'
        # f' | r: {format_count(stats["run_once_triggers"])} / {format_count(stats["skip_run_once_triggers"])}'
    )


def format_data(data):
    sent, received = 0, 0
    if "sent" in data:
        sent = data["sent"]

    if "received" in data:
        received = data["received"]

    return f"{format_file_size(sent)} / {format_file_size(received)}"


def format_messages(messages):
    sent, received = 0, 0
    if "sent" in messages:
        sent = messages["sent"]

    if "received" in messages:
        received = messages["received"]

    return f"{format_count(sent)} / {format_count(received)}"


def metric(value: float, unit: str = "", precision: int = 3) -> str:
    if not math.isfinite(value):
        return humanize._format_not_finite(value)  # type: ignore
    exponent = int(math.floor(math.log10(abs(value)))) if value != 0 else 0

    if exponent >= 33 or exponent < -30:
        return humanize.scientific(value, precision - 1) + unit

    value /= 10 ** (exponent // 3 * 3)
    if exponent >= 3:
        ordinal_ = "kMGTPEZYRQ"[exponent // 3 - 1]
    elif exponent < 0:
        ordinal_ = "mμnpfazyrq"[(-exponent - 1) // 3]
    else:
        ordinal_ = ""
    value_ = format(value, ".%if" % max(0, precision - (exponent % 3) - 1))
    if not (unit or ordinal_) or unit in ("°", "′", "″"):
        space = ""
    else:
        space = " "

    return f"{value_}{space}{ordinal_}{unit}"


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
        self.max_tasks = 0
        super().__init__(
            formatters={
                "total_bytes_received": format_file_size,
                "total_bytes_sent": format_file_size,
                "messages s/r": format_messages,
                "asyncio": format_asyncio_stats,
                "data s/r": format_data,
                "latency": format_time,
            }
        )

    def to_tree(self):
        self.asyncio_stats()

        # if logger.isEnabledFor(log_levels.TRACE):
        if logger.isEnabledFor(5):
            self.stats["gc"] = self.gc_stats()
        return super().to_tree()

    def asyncio_stats(self):
        tasks = len(asyncio.tasks._all_tasks)
        if tasks > self.stats["asyncio"]["max_tasks"]:
            self.stats["asyncio"]["max_tasks"] = tasks

        self.stats["asyncio"]["tasks"] = tasks

        # return {
        #     "total_tasks_count": getattr(self.loop, "total_tasks_count", 0),
        #     "call_soon_count": getattr(self.loop, "call_soon_count", 0),
        #     "loop_iters": getattr(self.loop, "loop_iters", 0),
        #     "loop_inner_iters": getattr(self.loop, "loop_inner_iters", 0),
        #     "loop_queue": {
        #         "min": None,
        #         "max": 0,
        #         "avg": MovingAverage(maxlen=200),
        #     },
        # }

    def gc_stats(self):
        return gc.get_stats()

    def reset(self):
        super().reset()
        self.stats["asyncio"] = {
            "max_tasks": 0,
            "loop_iters": 0,
            "loop_reiters": 0,
            "loop_inner_iters": 0,
            "ready": 0,
            "total_tasks_count": 0,
            "call_soon_count": 0,
            "call_later_count": 0,
            "ntodo": 0,
        }

        # self.enabled = logging.root.getEffectiveLevel() <= logging.DEBUG

    def stat(self, s: NestedDict[str, float]) -> NestedDict[str, float]:
        """
        Compute statistics on the input dictionary.

        Args:
            s (NestedDict[str, float]): A nested dictionary of float values.

        Returns:
            NestedDict[str, float]: A nested dictionary of statistics computed on the input dictionary.
        """
        return s

    def latency(self, ts: int) -> NestedDict[str, float]:  # pyright: ignore
        l: int = time.time_ns() // 1000 - ts
        if l <= 0:
            return {}

        if "latency" not in self.stats:
            self.stats["latency"] = {  # pyright: ignore
                "min": None,
                "max": 0,
                "avg": MovingAverage(maxlen=200),
            }

        self.stats["latency"]["avg"].append(l)
        self.stats["latency"]["min"] = min(l, self.stats["latency"]["min"]) if self.stats["latency"]["min"] else l  # pyright: ignore
        self.stats["latency"]["max"] = max(l, self.stats["latency"]["max"]) if self.stats["latency"]["max"] else l  # pyright: ignore

        return {}

    def sent_to(self, pid: int, msg: bytes) -> NestedDict[str, float]:
        """
        Updates the statistics for a message sent to a specific peer.

        Args:
            pid (int): The ID of the peer the message was sent to.
            msg (bytes): The message that was sent.

        Returns:
            A dictionary containing the updated statistics.
        """

        return {
            "messages s/r": {
                "sent": +1,
            },
            "data s/r": {
                "sent": +len(msg),
            },
            # "messages": +1,
            # f"messages_sent_to[{pid}]": +1,
            # "total_bytes_sent": +len(msg),
            # f"bytes_sent_to[{pid}]": +len(msg),
        }

    def received_from(self, pid: int, msg: bytes) -> NestedDict[str, float]:
        """
        Records statistics for a message received from a given party.

        Args:
            pid (int): The ID of the party that sent the message.
            msg (bytes): The message that was received.

        Returns:
            A dictionary containing the following statistics:
            - total_messages_received: The total number of messages received.
            - messages_received_from[pid]: The number of messages received from the given party.
            - total_bytes_received: The total number of bytes received.
            - bytes_received_from[pid]: The number of bytes received from the given party.
        """
        return {
            "messages s/r": {
                "received": +1,
            },
            "data s/r": {
                "received": +len(msg),
            },
            # "total_messages_received": +1,
            # f"messages_received_from[{pid}]": +1,
            # "total_bytes_received": +len(msg),
            # f"bytes_received_from[{pid}]": +len(msg),
        }


stats = StatsCollector()
