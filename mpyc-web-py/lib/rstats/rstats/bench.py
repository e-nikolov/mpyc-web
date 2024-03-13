# pylint: disable-all

import ast
import asyncio
import gc
import inspect
import itertools
import logging
import sys
import textwrap
import time
from contextlib import ContextDecorator
from functools import wraps
from typing import Awaitable, Callable, Concatenate, ParamSpec, Sized, TypeGuard, TypeVar, overload

import rich

from .bench_ast import make_timeit_source, parse_func_ast
from .bench_context import transform_ast_func
from .context import GCManager
from .format import format_args, format_ops, metric
from .types import AsyncCallable, MaybeAsyncCallable, R, TimerFunc, isasynccallable, isnotasynccallable

if len(logging.root.handlers) == 0:
    logging.basicConfig(level=logging.INFO)


default_iterations = 1000000
default_best_of = 2
default_min_duration = 0.2
default_timer = time.time


# type BenchFunc[P] = Callable[Concatenate[int, TimerFunc, P], float]
type MaybeAsyncBenchFunc[**P] = MaybeAsyncCallable[Concatenate[int, TimerFunc, P], float]
type AsyncBenchFunc[**P] = AsyncCallable[Concatenate[int, TimerFunc, P], float]
type SyncBenchFunc[**P] = Callable[Concatenate[int, TimerFunc, P], float]

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


class bench:
    def __init__(self, label=None, _globals=None, best_of=default_best_of, verbose=False, min_duration=default_min_duration, timer: TimerFunc = default_timer):
        self.label = label
        self._globals = _globals
        self.best_of = best_of
        self.verbose = verbose
        self.min_duration = min_duration
        self.timer = timer

    @overload
    def __call__(self, func: AsyncCallable[P, R]) -> AsyncCallable[P, R]: ...

    @overload
    def __call__(self, func: Callable[P, R]) -> Callable[P, R]: ...

    def __call__(self, func: MaybeAsyncCallable[P, R]) -> MaybeAsyncCallable[P, R]:
        if isasynccallable(func):
            return self._bench_async(func)
        elif isnotasynccallable(func):
            return self._bench_sync(func)

        raise TypeError("Invalid function type")

    def _bench_sync(
        self,
        func: Callable[P, R],
    ):
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            bench_func = self.to_bench_func(func, _globals=get_caller_globals(self._globals))
            ss = self.autorange(*args, **kwargs)
            iterations = ss.send(None)
            while True:
                try:
                    iterations = ss.send(bench_func(iterations, self.timer, *args, **kwargs))
                except StopIteration:
                    return func(*args, **kwargs)

        return wrapper

    def _bench_async(
        self,
        func: AsyncCallable[P, R],
    ) -> AsyncCallable[P, R]:

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            bench_func = self.to_bench_func(func, _globals=get_caller_globals(self._globals))
            ss = self.autorange()
            iterations = ss.send(None)
            while True:
                try:
                    iterations = ss.send(await bench_func(iterations, self.timer, *args, **kwargs))
                except StopIteration:
                    return await func(*args, **kwargs)

        return wrapper

    def autorange(self, *args, **kwargs):
        min_time_taken = float("inf")

        for _ in range(self.best_of):
            i = 1
            while True:
                for j in 1, 2, 5:
                    iterations = i * j
                    with GCManager():
                        time_taken = yield iterations

                    if time_taken >= self.min_duration:
                        min_time_taken = min(min_time_taken, time_taken / iterations)
                        break
                else:
                    i *= 10
                    continue
                break
        self.print_bench(min_time_taken, args=args, kwargs=kwargs)

    @overload
    def to_bench_func(self, func: AsyncCallable[P, R], _globals) -> AsyncBenchFunc[P]: ...

    @overload
    def to_bench_func(self, func: Callable[P, R], _globals) -> SyncBenchFunc[P]: ...

    def to_bench_func(self, func: MaybeAsyncCallable[P, R], _globals=None) -> MaybeAsyncBenchFunc[P]:
        func_name = f"___bench_{func.__name__}"
        src = make_timeit_source(func_name, func)
        if self.verbose:
            logging.info(src)
        local_ns = {}
        exec(compile(src, "<timeit-src>", "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT), _globals, local_ns)
        return local_ns[func_name]

    def print_bench(self, time, tabsize=20, args=[], kwargs={}):
        label = f"{self.label}{format_args(*args, **kwargs)}:"
        logging.info(f"{self.label:<{tabsize}}{metric(time, 's', skip_trailing_zeroes=False):>{8}} {format_ops(1/time):>{tabsize}}")


def get_caller_globals(_globals):
    g = sys._getframe(2).f_globals if _globals is None else _globals()
    return g | {"itertools": globals()["itertools"]}
