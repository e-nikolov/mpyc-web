# pylint: disable-all

import ast
import asyncio
import gc
import inspect
import itertools
import logging
import textwrap
import time
from contextlib import ContextDecorator
from functools import partial, wraps
from typing import Any, Awaitable, Callable, Concatenate, Coroutine, Iterable, Iterator, ParamSpec, Sized, TypeGuard, TypeVar, Union, overload

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

AsyncCallable = Callable[P, Awaitable[R]]
MaybeAsyncCallable = AsyncCallable[P, R] | Callable[P, R]
# loop = asyncio.get_event_loop()


def to_closure(func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> Callable[[], R]:
    return wraps(func)(partial(func, *args, **kwargs))


def isasynccallable(func: MaybeAsyncCallable[P, R]) -> TypeGuard[AsyncCallable[P, R]]:
    return asyncio.iscoroutinefunction(func)


def isnotasynccallable(func: MaybeAsyncCallable[P, R]) -> TypeGuard[Callable[P, R]]:
    return not asyncio.iscoroutinefunction(func)


default_iterations = 1000000
default_repeat = 5
default_timer = time.perf_counter


try:
    import gc

    default_disable_gc = True
except:
    default_disable_gc = False


class TimeitManager(ContextDecorator):
    def __init__(self, timer: Callable[[], float] = default_timer, disable_gc=default_disable_gc):
        self.timer = timer
        self.disable_gc = disable_gc

    def __enter__(self):
        if self.disable_gc:
            self.gcold = gc.isenabled()
            gc.disable()
        self.start_time = self.timer()
        return self

    def __exit__(self, *exc):
        self.timing: float = self.timer() - self.start_time
        if self.disable_gc and self.gcold:
            gc.enable()


def autorange_generator():
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            yield iterations
        i *= 10


async def autorange_async(func: AsyncCallable[P, R], *args: P.args, **kwargs: P.kwargs) -> tuple[float, R]:
    for iterations in autorange_generator():
        if args or kwargs:
            with TimeitManager() as tm:
                res = await func(*args, **kwargs)
                for _ in itertools.repeat(None, iterations - 1):
                    await func(*args, **kwargs)

            if tm.timing >= 0.2:
                return iterations / tm.timing, res
        else:
            with TimeitManager() as tm:
                res = await func()
                for _ in itertools.repeat(None, iterations - 1):
                    await func()

            if tm.timing >= 0.2:
                return iterations / tm.timing, res

    raise ValueError("autorange_sync: no result")


def autorange_sync(func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> tuple[float, R]:
    for iterations in autorange_generator():
        if args or kwargs:
            with TimeitManager() as tm:
                res = func(*args, **kwargs)
                for _ in itertools.repeat(None, iterations - 1):
                    func(*args, **kwargs)
            if tm.timing >= 0.2:
                return iterations / tm.timing, res
        else:
            with TimeitManager() as tm:
                res = func()
                for _ in itertools.repeat(None, iterations - 1):
                    # x = (*args,)
                    func()
            if tm.timing >= 0.2:
                return iterations / tm.timing, res

    raise ValueError("autorange_sync: no result")


def _bench_async(func: AsyncCallable[P, R]) -> AsyncCallable[P, R]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs):
        h = to_closure(func, *args, **kwargs)
        maxOpS = 0.0
        for _ in range(3):
            ops, res = await autorange_async(func, *args, **kwargs)
            maxOpS = max(maxOpS, ops)
        print_bench(func.__name__, maxOpS, *args, **kwargs)
        return res

    return wrapper


def _bench_sync(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        h = to_closure(func, *args, **kwargs)
        maxOpS = 0.0

        for _ in range(1):
            ops, res = autorange_sync(func, *args, **kwargs)
            maxOpS = max(maxOpS, ops)
        print_bench(func.__name__, maxOpS, *args, **kwargs)
        return res

    return wrapper


def bench(a, b, c):
    @overload
    def _bench(func: AsyncCallable[P, R]) -> AsyncCallable[P, R]: ...

    @overload
    def _bench(func: Callable[P, R]) -> Callable[P, R]: ...

    def _bench(func: MaybeAsyncCallable[P, R]) -> MaybeAsyncCallable[P, R]:
        if isasynccallable(func):
            return _bench_async(func)
        elif isnotasynccallable(func):
            return _bench_sync(func)

        raise TypeError("Invalid function type")

    return _bench


def format_ops(ops: float) -> str:
    return f"{round(ops):,} ops/sec"


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


def print_bench(label: str, ops: float, *args, **kwargs):
    logging.info(f"{label}{format_args(*args, **kwargs)}: {format_ops(ops)}")
