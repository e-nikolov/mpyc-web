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

timer = time.time
from .bench_ast import make_timeit_source, parse_func_ast
from .bench_context import transform_ast_func
from .format import format_ops, metric
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


def bench(label=None, _globals=None, best_of=default_best_of, verbose=False, min_duration=default_min_duration, timer: Callable[[], float] = default_timer):
    @overload
    def _bench(func: AsyncCallable[P, R]) -> AsyncCallable[P, R]: ...

    @overload
    def _bench(func: Callable[P, R]) -> Callable[P, R]: ...

    def _bench(func: MaybeAsyncCallable[P, R]) -> MaybeAsyncCallable[P, R]:
        if isasynccallable(func):
            return _bench_async(func, label=label, _globals=_globals, best_of=best_of, verbose=verbose, min_duration=min_duration, timer=timer)
        elif isnotasynccallable(func):
            return _bench_sync(func, label=label, _globals=_globals, best_of=best_of, verbose=verbose, min_duration=min_duration, timer=timer)

        raise TypeError("Invalid function type")

    return _bench


def _bench_sync(
    func: Callable[P, R],
    label=None,
    _globals=None,
    best_of=default_best_of,
    verbose=False,
    min_duration=default_min_duration,
    timer: Callable[[], float] = default_timer,
):
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        bench_func = to_bench_func(func, _globals=get_caller_globals(_globals))
        ss = autorange_generator(*args, **kwargs)
        iterations = ss.send(None)
        while True:
            try:
                iterations = ss.send(bench_func(iterations, timer, *args, **kwargs))
            except StopIteration:
                return func(*args, **kwargs)

    return wrapper


async def _bench_async(
    func: AsyncCallable[P, R],
    label=None,
    _globals=None,
    best_of=default_best_of,
    verbose=False,
    min_duration=default_min_duration,
    timer: Callable[[], float] = default_timer,
) -> AsyncCallable[P, R]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs):
        bench_func = to_bench_func(func, _globals=get_caller_globals(_globals))
        ss = autorange_generator(*args, **kwargs)
        iterations = ss.send(None)
        while True:
            try:
                iterations = ss.send(await bench_func(iterations, timer, *args, **kwargs))
            except StopIteration:
                return await func(*args, **kwargs)

    return wrapper


@overload
def to_bench_func(func: AsyncCallable[P, R], _globals) -> AsyncBenchFunc[P]: ...


@overload
def to_bench_func(func: Callable[P, R], _globals) -> SyncBenchFunc[P]: ...


def to_bench_func(func: MaybeAsyncCallable[P, R], _globals=None) -> MaybeAsyncBenchFunc[P]:
    func_name = f"___bench_{func.__name__}"
    src = make_timeit_source(func_name, func)

    local_ns = {}
    exec(compile(src, "<timeit-src>", "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT), _globals, local_ns)
    return local_ns[func_name]


def autorange_generator(*args, **kwargs):
    min_time_taken = float("inf")

    for _ in range(3):
        i = 1
        while True:
            for j in 1, 2, 5:
                iterations = i * j
                with GCManager():
                    time_taken = yield iterations

                if time_taken >= 0.2:
                    min_time_taken = min(min_time_taken, time_taken / iterations)
                    break
            else:
                i *= 10
                continue
            break
    print_bench(min_time_taken, args=args, kwargs=kwargs)


def print_bench(label, time, tabsize=20, args=[], kwargs={}):
    label = f"{ label}{format_args(*args, **kwargs)}:"
    logging.info(f"{ label:<{tabsize}}{metric(time, 's', skip_trailing_zeroes=False):>{8}} {format_ops(1/time):>{tabsize}}")


try:
    import gc

    default_disable_gc = True
except:
    default_disable_gc = False


class GCManager(ContextDecorator):
    def __init__(self, disable_gc=default_disable_gc):
        # def __init__(self, func, _globals, iters, disable_gc=default_disable_gc):
        self.disable_gc = disable_gc
        # self.runnable = make_runnable(func, _globals)

    def __enter__(self):
        if self.disable_gc:
            self.gcold = gc.isenabled()
            gc.disable()

        # self.runnable = make_runnable()
        return self

    def __exit__(self, *exc):
        if self.disable_gc and self.gcold:
            gc.enable()


def get_caller_globals(_globals):
    g = sys._getframe(2).f_globals if _globals is None else _globals()
    return g | {"itertools": globals()["itertools"]}


def reindent(src, indent):
    """Helper to reindent a multi-line statement."""
    return src.replace("\n", "\n" + " " * indent)


def _repr(arg):
    if isinstance(arg, Sized):
        l = len(arg)
        if l > 10:
            return f"{type(arg).__name__}[{l}]"
        return repr(arg)
    else:
        return repr(arg)


def format_args(*args, **kwargs):
    args_repr = [_repr(arg) for arg in args]
    kwargs_repr = [f"{key}={repr(value)}" for key, value in kwargs.items()]
    args_fmt = ", ".join(args_repr + kwargs_repr)
    if args_fmt != "":
        args_fmt = f"({args_fmt})"
    return args_fmt
