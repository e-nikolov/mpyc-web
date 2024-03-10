# pylint: disable-all

import asyncio
import collections
import gc
import inspect
import itertools
import logging
import sys
import time
import timeit
from contextlib import ContextDecorator, contextmanager
from functools import partial, reduce, wraps
from inspect import isawaitable, isfunction
from types import FrameType
from typing import Any, Awaitable, Callable, ParamSpec, TypeGuard, TypeVar, overload

if len(logging.root.handlers) == 0:
    logging.basicConfig(level=logging.INFO)

gc.disable()
default_min_duration = 0.2
default_best_of = 3
default_iterations = 1000000
default_timer = time.perf_counter


type AsyncCallable[**P, R] = Callable[P, Awaitable[R]]
type MaybeAsyncCallable[**P, R] = AsyncCallable[P, R] | Callable[P, R]


@overload
def to_handle[**P, R](func: AsyncCallable[P, R], *args: P.args, **kwargs: P.kwargs) -> AsyncCallable[[], R]: ...


@overload
def to_handle[**P, R](func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> Callable[[], R]: ...


def to_handle[**P, R](func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> Callable[[], R]:
    return wraps(func)(partial(func, *args, **kwargs))


class TimeitManager(ContextDecorator):
    def __init__(self, timer: Callable[[], float] = default_timer):
        self.timer = timer

    def __enter__(self):
        self.start_time = self.timer()
        return self

    def __exit__(self, *exc):
        self.timing: float = self.timer() - self.start_time


def isasynccallable[**P, R](__obj: MaybeAsyncCallable[P, R]) -> TypeGuard[AsyncCallable[P, R]]:
    return asyncio.iscoroutinefunction(__obj)


def isnotasynccallable[**P, R](__obj: MaybeAsyncCallable[P, R]) -> TypeGuard[Callable[P, R]]:
    return not asyncio.iscoroutinefunction(__obj)


@overload
def timeit[R](func: AsyncCallable[[], R], iterations: int = default_iterations, timer: Callable[[], float] = default_timer) -> Awaitable[tuple[float, R]]: ...


@overload
def timeit[R](func: Callable[[], R], iterations: int = default_iterations, timer: Callable[[], float] = default_timer) -> tuple[float, R]: ...


def timeit[R](func: MaybeAsyncCallable[[], R], iterations=default_iterations, timer=default_timer) -> tuple[float, R] | Awaitable[tuple[float, R]]:
    res = None
    if isasynccallable(func):

        async def atimeit() -> tuple[float, Any]:
            with TimeitManager(timer) as tm:
                res = await func()
                for _ in itertools.repeat(None, iterations - 1):
                    await func()
            return tm.timing, res

        return atimeit()
    elif isnotasynccallable(func):
        with TimeitManager(timer) as tm:
            res = func()
            for _ in itertools.repeat(None, iterations - 1):
                func()
        return tm.timing, res
    else:
        raise ValueError("func is not a callable")


def autorange_generator():
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            yield iterations
        i *= 10


def autorange_sync[R](func: Callable[[], R], min_duration=default_min_duration) -> tuple[float, R]:
    for iterations in autorange_generator():
        time_taken, res = timeit(func, iterations)
        if time_taken >= min_duration:
            return iterations / time_taken, res
    raise ValueError("autorange_sync: no result")


async def autorange_async[R](func: AsyncCallable[[], R], min_duration=default_min_duration) -> tuple[float, R]:
    for iterations in autorange_generator():
        time_taken, res = await timeit(func, iterations)
        if time_taken >= min_duration:
            return iterations / time_taken, res
    raise ValueError("autorange_async: no result")


class bench[**P, R](ContextDecorator):
    def __init__(
        self,
        label: str | None = None,
        best_of=default_best_of,
        min_duration=default_min_duration,
        timer=default_timer,
    ):
        self.label = label
        self.best_of = best_of
        self.min_duration = min_duration
        self.timer = timer
        self.func: Callable | None = None
        self.args = []
        self.kwargs = {}

        self.ops = 0.0

    def _recreate_cm(self):
        """Return a recreated instance of self.

        Allows an otherwise one-shot context manager like
        _GeneratorContextManager to support use as
        a decorator via implicit recreation.

        This is a private interface just for _GeneratorContextManager.
        See issue #11647 for details.
        """
        return self

    def __call__(self, func: MaybeAsyncCallable[P, R]):
        self.label = self.label or func.__name__
        self.func = func

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            self.args = args
            self.kwargs = kwargs
            if isasynccallable(func):
                afunc = func
            else:

                async def afunc():
                    return func(*args, **kwargs)

            with self._recreate_cm():
                self.ops, res = await autorange_async(afunc)
                return res

        return wrapper

    def __enter__(self):
        self.label = self.label or label_from_frame(sys._getframe())
        if self.func is None:
            self.start_time = self.timer()
        return self

    def __exit__(self, *exc):
        if self.func is None:
            self.ops = 1 / (self.timer() - self.start_time)

        print_bench(self.label or "default", self.ops, *self.args, **self.kwargs)
        self.ops = 0.0


async def to_async(func):
    return func()


def label_from_frame(frame: FrameType):
    f = frame.f_back

    if f is not None:
        func_name = f"{f.f_code.co_name}"
        if func_name == "<module>" or func_name == "<lambda>":
            func_name = ""
        else:
            func_name = f":{func_name}"

        return f"{f.f_code.co_filename}:{f.f_lineno}{func_name}"


def format_ops(ops: float) -> str:
    return f"{round(ops):,} ops/sec"


def _repr(arg):
    if isinstance(arg, list | dict | tuple | set | collections.deque):
        return f"{type(arg).__name__}[{len(arg)}]"
    else:
        return repr(arg)


def format_args(*args, **kwargs):
    args_repr = [_repr(arg) for arg in args]
    kwargs_repr = [f"{key}={repr(value)}" for key, value in kwargs.items()]
    args_fmt = ", ".join(args_repr + kwargs_repr)
    if args_fmt != "":
        args_fmt = f"({args_fmt})"
    return args_fmt


def print_bench(label: str, ops: float, *args, **kwargs):
    logging.info(f"{label}{format_args(*args, **kwargs)}: {format_ops(ops)}")
