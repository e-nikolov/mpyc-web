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
import io
import json
import logging
import math
import time
from ast import Num
from collections import deque
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Generic, ParamSpec, TypeVar

import humanize
import rich
import yaml
from humanize import naturalsize
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
T = TypeVar("T")

# pyright: ignore-all
# pylint: disable=all
# pyright: ignore=all
# type: ignore=all


class MovingAverage:
    def __init__(self, maxlen: int = 100):
        self._maxlen = maxlen
        self._ring = deque(maxlen=maxlen)
        self._total = 0

    def append(self, value: N):
        if len(self._ring) == self._maxlen:
            self._total -= self._ring.popleft()
        self._total += value
        self._ring.append(value)

    def __len__(self):
        return len(self._ring)

    def __float__(self):
        return self._total / len(self._ring)


class DeepCounter(NestedDict[K, Numeric | Any]):
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

    def set_path(self, path: str, value: Numeric):
        keys = path.split(".")
        d = self
        for key in keys[:-1]:
            # Create a nested dictionary if key does not exist
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def acc_path(self, path: str, value: Numeric):
        keys = path.split(".")
        d = self
        for key in keys[:-1]:
            # Create a nested dictionary if key does not exist
            d = d.setdefault(key, {})
        d.setdefault(keys[-1], 0)
        d[keys[-1]] += value

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

    def update(self, iterable: NestedDict[K, Numeric]):
        self._update_recursive(self, iterable)

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


def format_time(time):
    # return f'{_format_time(time["min"])} / {_format_time(time["mavg"])} / {_format_time(time["avg"])} / {_format_time(time["max"])}'
    return f'{_format_time(time["min"])} / {_format_time(float(time["avg"]))} / {_format_time(time["max"])}'


def _format_time(time: Numeric):
    return metric(time / 1_000_000, "s")


def format_file_size(size):
    return naturalsize(size, binary=True)


def format_count(count, unit=""):
    return metric(count, unit=unit, precision=0)
    # return humanize.intword(count)


FUNC_ARG: str = "$func"
TIME_ARG: str = "$time"


class BaseStatsCollector:
    """
    A base class for collecting statistics.

    Attributes:
        stats (DeepCounter[str]): A counter object for storing the statistics.
        enabled (bool): A flag indicating whether the statistics collection is enabled.
    """

    def __init__(self, formatters: dict[str, Callable[[str], str]] = {}):
        self.enabled = False
        self.start_time = datetime.now()
        self.stats = DeepCounter[str]({})
        self.loop = asyncio.get_event_loop()
        self.formatters = {
            "time": format_time,
        } | formatters

    def set_path(self, path: str, value: Any):
        if self.enabled:
            self.stats.set_path(path, value)

    def acc_path(self, path: str, value: Any):
        if self.enabled:
            self.stats.acc_path(path, value)

    def dec(
        self, counter_func: Callable[P, NestedDict[str, Numeric]], update_func: Callable[[], Callable[[NestedDict[str, Numeric]], None]]
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

                d: NestedDict[str, Numeric] = counter_func(*args, **kwargs)
                if FUNC_ARG in d:
                    f_name = func.__name__
                    func_stats = d.pop(FUNC_ARG)
                    d |= {f_name: func_stats}

                    if f_name not in self.stats:  # pyright: ignore
                        self.stats[f_name] = {}  # pyright: ignore

                    if "time" not in self.stats[f_name]:  # pyright: ignore
                        self.stats[f_name]["time"] = {  # pyright: ignore
                            "min": None,
                            "max": None,
                            "avg": MovingAverage(maxlen=200),
                        }

                    self.stats[f_name]["time"]["avg"].append(elapsed_time)  # pyright: ignore
                    self.stats[f_name]["time"]["min"] = (  # pyright: ignore
                        min(elapsed_time, self.stats[f_name]["time"]["min"])  # pyright: ignore
                        if self.stats[f_name]["time"]["min"]  # pyright: ignore
                        else elapsed_time  # pyright: ignore
                    )
                    self.stats[f_name]["time"]["max"] = (  # pyright: ignore
                        max(elapsed_time, self.stats[f_name]["time"]["max"])  # pyright: ignore
                        if self.stats[f_name]["time"]["max"]  # pyright: ignore
                        else elapsed_time  # pyright: ignore
                    )
                update_func()(d)
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
        return self.dec(counter_func, lambda: self.stats.update)

    def reset(self):
        """
        Resets the statistics counter and enables statistics collection.
        """
        self.stats = DeepCounter[str]({})
        self.start_time = datetime.now()
        self.loop = asyncio.get_event_loop()

    def to_tree(self):
        if not self.enabled:
            return ""
        tree = Tree("", style="gray50", hide_root=True)
        self._to_tree(self.stats, tree)

        return rich_to_ansi(Panel.fit(tree, title="stats", subtitle=time_delta_fmt(datetime.now(), self.start_time), border_style="blue"))

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

    def time(self) -> NestedDict[str, float]:
        """
        A decorator function for accumulating statistics.

        Args:
            counter_func (Callable[P, NestedDict[str, Numeric]]): A function that returns a dictionary of statistics.

        Returns:
            Callable[[Callable[P, R]], Callable[P, R]]: A decorated function that accumulates statistics.
        """
        return {FUNC_ARG: {}}

    # def avg(self, name: str, value: Numeric = 1):
    #     """
    #     A decorator function for accumulating statistics.

    #     Args:
    #         counter_func (Callable[P, NestedDict[str, Numeric]]): A function that returns a dictionary of statistics.

    #     Returns:
    #         Callable[[Callable[P, R]], Callable[P, R]]: A decorated function that accumulates statistics.
    #     """
    #     if name not in self.stats:
    #         self.stats[name] = MovingAverage(maxlen=200)

    #     return self.stats[name].append(value)

    def total_calls(self) -> NestedDict[str, float]:
        """
        Returns a dictionary with a single key-value pair, where the key is "self.func" and the value is another dictionary
        with a single key-value pair, where the key is "calls" and the value is +1. This method is used to track the total
        number of calls to a function.
        """
        return {FUNC_ARG: {"calls": +1}}
