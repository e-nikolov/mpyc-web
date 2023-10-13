import logging

from pathlib import Path
import sys
from typing import Optional, TypeVar, Any, Callable, ParamSpec
from functools import wraps


# pyright: reportMissingImports=false
logger = logging.getLogger(__name__)


# called at the end of this file
def __init__():
    global stats
    stats = StatsCollector()


K = TypeVar("K")
V = TypeVar("V")

NestedDict = dict[K, V | "NestedDict[K, V]"]

Numeric = int | float

N = TypeVar("N", int, float)


class DeepCounter(NestedDict[K, Numeric]):
    def update(self, iterable: NestedDict[K, Numeric]):
        self._update_recursive(self, iterable)

    def set(self, iterable: NestedDict[K, Numeric]):
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


class BaseStatsCollector:
    stats = DeepCounter[str]({})
    enabled = logging.root.getEffectiveLevel() <= logging.DEBUG

    def dec(
        self, counter_func: Callable[P, NestedDict[str, Numeric]], ff: Callable[[], Callable[[NestedDict[str, Numeric]], None]]
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                if self.enabled:
                    d = counter_func(*args, **kwargs)
                    if "$func" in d:
                        d["$func"] = {func.__name__: d.pop("$func")}
                    ff()(d)
                return func(*args, **kwargs)

            return wrapper

        return decorator

    # def set(self, counter_func: Callable[P, NestedDict[str, Numeric]]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    #     return self.dec(counter_func, lambda: self.stats.set)

    def acc(self, counter_func: Callable[P, NestedDict[str, Numeric]]) -> Callable[[Callable[P, R]], Callable[P, R]]:
        return self.dec(counter_func, lambda: self.stats.update)

    def reset(self):
        self.stats = DeepCounter[str]()
        self.enabled = logging.root.getEffectiveLevel() <= logging.DEBUG

    def print_stats(self):
        if self.enabled:
            print(self.stats)


class StatsCollector(BaseStatsCollector):
    def stat(self, s: NestedDict[str, float]) -> NestedDict[str, float]:
        return s

    def total_calls(self) -> NestedDict[str, float]:
        return {"$func": {"calls": +1}}

    def sent_to(self, pid: int, msg: bytes) -> NestedDict[str, float]:
        return {
            f"total_messages_sent": +1,
            f"messages_sent_to[{pid}]": +1,
            f"total_bytes_sent": +len(msg),
            f"bytes_sent_to[{pid}]": +len(msg),
        }

    def received_from(self, pid: int, msg: bytes) -> NestedDict[str, float]:
        return {
            f"total_messages_received": 1,
            f"messages_received_from[{pid}]": 1,
            f"total_bytes_received": len(msg),
            f"bytes_received_from[{pid}]": len(msg),
        }


__init__()
