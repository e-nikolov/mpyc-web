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
import inspect
import io
import json
import logging
import math
import sys
import time
from collections import deque
from contextlib import ContextDecorator
from datetime import datetime
from enum import StrEnum, auto
from functools import wraps
from typing import Any, Callable, Generic, Mapping, MutableMapping, ParamSpec, TypeAlias, TypeAliasType, TypedDict, TypeVar

import humanize
import rich
import yaml
from humanize import naturalsize
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

from .avg import MovingAverage
from .counter import DeepCounter
from .format import format_count, format_file_size, rich_to_ansi, time_delta_fmt
from .time import TimeStats
from .types import NestedDict, Numeric

# type: ignore-all
logger = logging.getLogger(__name__)

__all__ = [
    "MovingAverage",
]
# pyright: ignore-all
# pylint: disable=all
# pyright: ignore=all
# type: ignore=all


FUNC_ARG: str = "$func"
TIME_ARG: str = "$time"
DEFAULT_TIMER_LABEL: str = "default"


# P = ParamSpec("P")
# R = TypeVar("R")


class TimingStats(dict[str, TimeStats]):
    def update_timing(self, label: str, elapsed_time: float):
        if label not in self:
            self[label] = TimeStats()

        self[label].update(elapsed_time)

    def __str__(self):
        txt = ""
        for k, t in sorted(self.items()):
            txt += f"\n\t{k}: {str(t)}"
        return txt


class BaseStatsState:
    # __dict__ = DeepCounter[str]({})

    def __init__(self):
        self.__dict__ = DeepCounter[str]({})
        self.timings = TimingStats()


def has_to_string(obj):
    return type(obj).__str__ is not object.__str__


class BaseStatsCollector[**P, R]:
    enabled = False
    start_time = datetime.now()

    def __init__(
        self,
        formatters: dict[str, Callable[[str], str]] = {},
        on_before_get_stats_hooks: list[Callable[["BaseStatsCollector[P, R]"], None]] = [],
        state=BaseStatsState(),
    ):
        self.state = state

        self.on_before_get_stats_hooks = on_before_get_stats_hooks
        # self.formatters = {
        #     TIME_ARG: format_times,
        # } | formatters
        self.formatters = formatters

    def get_path(self, *path: str, default=None):
        return self.state.__dict__.get_path(*path, default=default)

    def set_path(self, value: Any, *path: str):
        if self.enabled:
            self.state.__dict__.set_path(value, *path)

    def acc_path(self, value: Any, *path: str):
        if self.enabled:
            self.state.__dict__.acc_path(value, *path)

    def time(self, label="default"):
        return TimingContext(self, label)

    def reset(self, state=BaseStatsState()):
        """
        Resets the statistics counter and enables statistics collection.
        """
        self.state = state
        self.start_time = datetime.now()

    def __str__(self):
        if not self.enabled:
            return ""

        tree = Tree("", style="gray50", hide_root=True)
        self._to_tree(self.get_stats(), tree)

        return rich_to_ansi(Panel.fit(tree, title="stats", subtitle=time_delta_fmt(datetime.now(), self.start_time), border_style="blue"))

    def _to_tree(self, s: dict | list[dict], tree: Tree):
        if isinstance(s, dict):
            for k, v in sorted(s.items()):
                if k in self.formatters:
                    tree.add(f"{k}: {self.formatters[k](v)}")
                elif has_to_string(v):
                    v_str = str(v)
                    if len(v_str) > 0:
                        tree.add(f"{k}: {v_str}")
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

    def get_stats(self):
        """
        Returns the statistics collected so far.

        Returns:
            dict: A dictionary containing the statistics collected so far.
        """
        for hook in self.on_before_get_stats_hooks:
            # print(hook, self)
            hook(self)

        self.state.__dict__[TIME_ARG] = self.state.timings

        # print(self.stats.counter)

        return self.state.__dict__

    def total_calls(self) -> NestedDict[str, float]:
        """
        Returns a dictionary with a single key-value pair, where the key is "self.func" and the value is another dictionary
        with a single key-value pair, where the key is "calls" and the value is +1. This method is used to track the total
        number of calls to a function.
        """
        return {FUNC_ARG: {"calls": +1}}


class TimingContext[**P, R](ContextDecorator):
    def __init__(self, stats: BaseStatsCollector[P, R], label="default"):
        self.stats = stats
        self.timings = None
        self.label = label

    def __call__(self, func, *args, **kwargs):  # only called when used as a decorator
        # print(func, args, kwargs)
        self.func = func
        if self.label is DEFAULT_TIMER_LABEL:
            self.label = func.__name__
        return super().__call__(func)

    def __enter__(self, *args, **kwargs):
        # print("__enter__", self, args, kwargs)
        if not self.stats.enabled:
            return

        if self.label is DEFAULT_TIMER_LABEL:
            f = sys._getframe().f_back
            if f is not None:
                f_name, line = f.f_code.co_name, f.f_lineno
                self.label = f"{f_name}:{line}"

        self.start_time = time.perf_counter_ns()

    def __exit__(self, *args):
        if not self.stats.enabled:
            return

        self.stats.state.timings.update_timing(self.label, (time.perf_counter_ns() - self.start_time) // 1000)
