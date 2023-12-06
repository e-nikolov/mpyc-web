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

The `__init__` function at the end of the module initializes a global `stats` object of type `StatsCollector`.
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

# type: ignore-all
logger = logging.getLogger(__name__)

K = TypeVar("K")
V = TypeVar("V")
NestedDict = dict[K, V | "NestedDict[K, V]"]

Numeric = int | float

N = TypeVar("N", int, float)

# pyright: ignore-all


class DeepCounter(NestedDict[K, Numeric]):
    """A nested dictionary that stores numeric values and supports recursive updates.

    This class extends the `NestedDict` class and adds two methods for updating its values:
    `set` and `update`. Both methods take a nested dictionary as input and update the values
    in the `DeepCounter` instance recursively, i.e., for each key in the input dictionary,
    the corresponding value is either added to the current value (for `update`) or replaced
    by the input value (for `set`).

    The `DeepCounter` class is parameterized by two type variables: `K` and `Numeric`.
    `K` represents the type of the keys in the nested dictionary, while `Numeric` represents
    the type of the numeric values that can be stored in the dictionary.

    Example usage:
    ```
    >>> counter = DeepCounter[int, float]()
    >>> counter.set({1: {2: 3.0}})
    >>> counter.update({1: {2: 1.5}})
    >>> counter
    {1: {2: 4.5}}
    ```
    """

    def update(self, iterable: NestedDict[K, Numeric]):
        self._update_recursive(self, iterable)

    def set(self, iterable: NestedDict[K, Numeric]):
        """
        Recursively sets the values of the nested dictionary to the values of the given iterable.

        Args:
            iterable (NestedDict[K, Numeric]): A nested dictionary containing the values to set.
        """
        self._set_recursive(self, iterable)

    def _set_recursive(self, target: NestedDict[K, Numeric], source: NestedDict[K, Numeric]):
        for key, value in source.items():
            if key in target:
                target_val = target[key]
                if isinstance(target_val, dict) and isinstance(value, dict):
                    self._set_recursive(target_val, value)
                elif isinstance(target_val, Numeric) and isinstance(value, Numeric):
                    target[key] = value
                else:
                    raise TypeError(f"Cannot set {type(value)} to {type(target[key])} for key {key}")
            else:
                target[key] = value

    def _update_recursive(self, target: NestedDict[K, Numeric], source: NestedDict[K, Numeric]):
        for key, value in source.items():
            if key in target:
                target_val = target[key]
                if isinstance(target_val, dict) and isinstance(value, dict):
                    self._update_recursive(target_val, value)
                elif isinstance(target_val, Numeric) and isinstance(value, Numeric):
                    target[key] = target_val + value
                else:
                    raise TypeError(f"Cannot add {type(value)} and {type(target_val)} for key {key}")
            else:
                target[key] = value


P = ParamSpec("P")
R = TypeVar("R")
import math


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


def print_to_string(*args, **kwargs):
    output = io.StringIO()
    rich.print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents


def rich_to_ansi(renderable):
    """Convert text formatted with rich markup to standard string."""
    if rich._console:
        with rich._console.capture() as capture:
            rich.print(renderable)
        return capture.get()


def time_delta_fmt(time_a, time_b):
    return datetime.utcfromtimestamp((time_a - time_b).total_seconds()).strftime("%X")


import datetime as dt


def format_time(time):
    # return f'{_format_time(time["min"])} / {_format_time(time["mavg"])} / {_format_time(time["avg"])} / {_format_time(time["max"])}'
    return f'{_format_time(time["min"])} / {_format_time(time["mavg"])} / {_format_time(time["max"])}'


def _format_time(time: Numeric):
    return metric(time / 1_000_000, "s")


def format_file_size(size):
    return naturalsize(size, binary=True)


def format_count(count, unit=""):
    return metric(count, unit=unit, precision=0)
    # return humanize.intword(count)


def format_asyncio_stats(stats):
    return (
        f'{format_count(stats["tasks"])} / {format_count(stats["max_tasks"])} tasks | {format_count(stats["call_later_count"])} /'
        f' {format_count(stats["call_immediate_count"])}'
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


FUNC_ARG: str = "$func"


class BaseStatsCollector:
    """
    A base class for collecting statistics.

    Attributes:
        stats (DeepCounter[str]): A counter object for storing the statistics.
        enabled (bool): A flag indicating whether the statistics collection is enabled.
    """

    stats = DeepCounter[str]({})
    enabled = False
    start_time = datetime.now()
    formatters: dict[str, Callable[[str], str]] = {
        "total_bytes_received": format_file_size,
        "total_bytes_sent": format_file_size,
        "time": format_time,
        "messages s/r": format_messages,
        "asyncio": format_asyncio_stats,
        "data s/r": format_data,
        "latency": format_time,
    }

    def dec(
        self, counter_func: Callable[P, NestedDict[str, Numeric]], update_func: Callable[[NestedDict[str, Numeric]], None]
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        A decorator function for collecting statistics.

        Args:
            counter_func (Callable[P, NestedDict[str, Numeric]]): A function that returns a dictionary of statistics.
            ff (Callable[[], Callable[[NestedDict[str, Numeric]], None]]): A function that returns a function for updating the statistics.

        Returns:
            Callable[[Callable[P, R]], Callable[P, R]]: A decorated function that collects statistics.
        """

        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                if not self.enabled:
                    return func(*args, **kwargs)

                start_time = time.perf_counter_ns()
                res = func(*args, **kwargs)
                elapsed_time = (time.perf_counter_ns() - start_time) // 1000

                d = counter_func(*args, **kwargs)
                if FUNC_ARG in d:
                    f_name = func.__name__
                    func_stats = d.pop(FUNC_ARG)
                    d |= {f_name: func_stats}

                    if f_name not in self.stats:  # pyright: ignore
                        self.stats[f_name] = {}  # pyright: ignore

                    if "time" not in self.stats[f_name]:  # pyright: ignore
                        self.stats[f_name]["time"] = {  # pyright: ignore
                            "calls": 0,
                            "total": 0,
                            "total_mavg": 0,
                            "mavg": 0,
                            "avg": 0,
                            "min": None,
                            "max": None,
                            "ring": deque(maxlen=200),
                        }

                    time_stats = self.stats[f_name]["time"]  # pyright: ignore
                    assert isinstance(time_stats, dict)
                    assert isinstance(time_stats["calls"], Numeric)
                    assert isinstance(time_stats["total"], Numeric)
                    assert isinstance(time_stats["min"], Numeric | None)
                    assert isinstance(time_stats["max"], Numeric | None)

                    calls = time_stats["calls"] + 1
                    total_time = time_stats["total"] + elapsed_time
                    total_mavg = time_stats["total_mavg"]
                    assert isinstance(total_mavg, Numeric)
                    ring = time_stats["ring"]
                    assert isinstance(ring, deque)

                    if len(ring) == ring.maxlen:
                        total_mavg -= ring.popleft()

                    total_mavg += elapsed_time
                    ring.append(elapsed_time)

                    time_stats["ring"] = ring
                    time_stats["calls"] = calls
                    time_stats["total"] = total_time
                    time_stats["total_mavg"] = total_mavg
                    time_stats["avg"] = total_time / calls
                    time_stats["mavg"] = total_mavg / len(ring)
                    time_stats["min"] = min(elapsed_time, time_stats["min"]) if time_stats["min"] else elapsed_time
                    time_stats["max"] = max(elapsed_time, time_stats["max"]) if time_stats["max"] else elapsed_time

                update_func(d)

                return res

            return wrapper

        return decorator

    def set(self, counter_func: Callable[P, NestedDict[str, Numeric]]) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        Sets the counter function for the statistics module.

        Args:
            counter_func: A callable function that takes a parameter of type P and returns a nested dictionary of string keys and numeric values.

        Returns:
            A callable function that takes a parameter of type R and returns a callable function that takes a parameter of type P and returns a value of type R.
        """
        return self.dec(counter_func, self.stats.set)

    def acc(self, counter_func: Callable[P, NestedDict[str, Numeric]]) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        A decorator function for accumulating statistics.

        Args:
            counter_func (Callable[P, NestedDict[str, Numeric]]): A function that returns a dictionary of statistics.

        Returns:
            Callable[[Callable[P, R]], Callable[P, R]]: A decorated function that accumulates statistics.
        """
        return self.dec(counter_func, self.stats.update)

    def reset(self):
        """
        Resets the statistics counter and enables statistics collection.
        """
        self.stats = DeepCounter[str]({})
        self.max_tasks = 0
        self.start_time = datetime.now()
        # self.enabled = logging.root.getEffectiveLevel() <= logging.DEBUG

    max_tasks = 0

    # @set(lambda self: {"asyncio": {"tasks": len(asyncio.all_tasks()), "max_tasks": self.stats.asyncio.max_tasks}})
    def asyncio_stats(self):
        loop = asyncio.get_event_loop()

        tasks = len(asyncio.all_tasks())
        if tasks > self.max_tasks:
            self.max_tasks = tasks

        return {
            "tasks": tasks,
            "max_tasks": self.max_tasks,
            "call_later_count": getattr(loop, "call_later_count", 0),
            "call_immediate_count": getattr(loop, "call_immediate_count", 0),
        }

    def gc_stats(self):
        return gc.get_stats()

    def to_tree(self):
        if not self.enabled:
            return ""

        # tree = Tree("", hide_root=True, highlight=True)
        tree = Tree("", style="gray50", hide_root=True)

        fstats = {}

        if len(self.stats) > 1:  # pyright: ignore
            fstats |= self.stats
            # self._to_tree(self.stats, tree.add("mpyc"))

        fstats["asyncio"] = self.asyncio_stats()
        # self._to_tree(self.asyncio_stats(), tree.add("asyncio"))

        if logger.isEnabledFor(log_levels.TRACE):
            fstats["gc"] = self.gc_stats()
            # self._to_tree(self.gc_stats(), tree.add("garbage_collector"))

        self._to_tree(fstats, tree)

        return rich_to_ansi(Panel.fit(tree, title="stats", subtitle=time_delta_fmt(datetime.now(), self.start_time), border_style="blue"))
        # return rich_to_ansi('[bold green]My[/][bold red]awesome[/][bold yellow]text[/]')
        # return print_to_string(tree)

    def _to_tree(self, s: dict | list[dict], tree: Tree):
        if isinstance(s, dict):
            for k, v in sorted(s.items()):
                if k in self.formatters:
                    tree.add(f"{k}: {self.formatters[k](v)}")
                elif isinstance(v, dict | list):
                    if len(v) > 0:
                        self._to_tree(v, tree.add(k))
                elif isinstance(v, int | float):
                    tree.add(f"{k}: {format_count(v)}")
                else:
                    tree.add(f"{k}: {v}")

        if isinstance(s, list):
            for index, item in enumerate(s):
                tree.add(f"{json.dumps(item)}")

    # def to_string(self):
    #     """
    #     Returns the collected statistics.
    #     """
    #     txt = ""
    #     if self.enabled:
    #         txt += f"{self.dumps('mpyc', self.stats)}\n"

    #         if logger.isEnabledFor(log_levels.TRACE):
    #             txt += f"{self.dumps('mpyc', self.stats)}\n"
    #             txt += f"{self.dumps('asyncio', {'tasks': len(asyncio.all_tasks())})}\n"
    #             gc.collect()
    #             txt += f"{self.dumps('gc', gc.get_stats())}\n"
    #     return txt

    def dumps(self, name, stats_data):
        """
        Convert stats_data to YAML format using json.dumps and yaml.safe_dump.

        Args:
            stats_data (dict): A dictionary containing statistics data.

        Returns:
            str: A YAML-formatted string representation of the stats_data dictionary.
        """
        return f"====== {name} ======\n{yaml.safe_dump(yaml.safe_load(json.dumps(stats_data)))}"

    def dump(self, name, stats_data, level=logging.DEBUG):
        """
        Dump the given stats data to the logger in JSON format.

        Args:
            stats_data (dict): A dictionary containing the stats data to be logged.
        """
        logger.log(level, self.dumps(name, stats_data), stacklevel=2)


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
        if l < 0:
            return {}

        if "latency" not in self.stats:
            self.stats["latency"] = {  # pyright: ignore
                "min": None,
                "max": 0,
                "total_mavg": 0,
                "ring": deque([], maxlen=200),
            }

        ring = self.stats["latency"]["ring"]  # pyright: ignore
        total_mavg = self.stats["latency"]["total_mavg"]  # pyright: ignore

        total_mavg += l  # pyright: ignore
        if len(ring) == ring.maxlen:  # pyright: ignore
            total_mavg -= ring.popleft()  # pyright: ignore
        ring.append(l)  # pyright: ignore

        if l > 0:
            self.stats["latency"]["min"] = min(l, self.stats["latency"]["min"]) if self.stats["latency"]["min"] else l  # pyright: ignore
            self.stats["latency"]["max"] = max(l, self.stats["latency"]["max"]) if self.stats["latency"]["max"] else l  # pyright: ignore

        self.stats["latency"]["ring"] = ring  # pyright: ignore
        self.stats["latency"]["total_mavg"] = total_mavg  # pyright: ignore
        self.stats["latency"]["mavg"] = total_mavg / len(ring)  # pyright: ignore

        return {}

    def time(self) -> NestedDict[str, float]:
        """
        A decorator function for accumulating statistics.

        Args:
            counter_func (Callable[P, NestedDict[str, Numeric]]): A function that returns a dictionary of statistics.

        Returns:
            Callable[[Callable[P, R]], Callable[P, R]]: A decorated function that accumulates statistics.
        """
        return {FUNC_ARG: {}}

    def total_calls(self) -> NestedDict[str, float]:
        """
        Returns a dictionary with a single key-value pair, where the key is "self.func" and the value is another dictionary
        with a single key-value pair, where the key is "calls" and the value is +1. This method is used to track the total
        number of calls to a function.
        """
        return {FUNC_ARG: {"calls": +1}}

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
