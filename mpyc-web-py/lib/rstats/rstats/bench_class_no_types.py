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
from .format import format_ops, metric

if len(logging.root.handlers) == 0:
    logging.basicConfig(level=logging.INFO)


default_iterations = 1000000
default_best_of = 2
default_min_duration = 0.2
default_timer = time.time


class bench:
    def __init__(self, label=None, _globals=None, best_of=default_best_of, verbose=False, min_duration=default_min_duration, timer=default_timer):
        self.label = label
        self._globals = _globals
        self.best_of = best_of
        self.verbose = verbose
        self.min_duration = min_duration
        self.timer = timer

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bench_func = self.to_bench_func(func, _globals=get_caller_globals(self._globals))
            if asyncio.iscoroutinefunction(func) and asyncio.iscoroutinefunction(bench_func):
                return self._bench_async(func, bench_func, *args, **kwargs)
            elif not asyncio.iscoroutinefunction(func) and not asyncio.iscoroutinefunction(bench_func):
                return self._bench_sync(func, bench_func, *args, **kwargs)

            raise TypeError("Invalid function type")

        return wrapper

    # def __call__(self, func):
    #     self.label = self.label or func.__name__
    #     bench_func = self.to_bench_func(func, _globals=get_caller_globals(self._globals))
    #     if isasynccallable(func) and isasynccallable(bench_func):
    #         return self._bench_async(func, bench_func)
    #     elif isnotasynccallable(func) and isnotasynccallable(bench_func):
    #         return self._bench_sync(func, bench_func)

    #     raise TypeError("Invalid function type")

    # def _bench(self, func):

    def _bench_sync(
        self,
        func,
        bench_func,
        *args,
        **kwargs,
    ):
        ss = self.autorange_generator(*args, **kwargs)
        iterations = ss.send(None)
        while True:
            try:
                iterations = ss.send(bench_func(iterations, self.timer, *args, **kwargs))
            except StopIteration:
                return func(*args, **kwargs)

        return wrapper

    async def _bench_async(
        self,
        func,
        bench_func,
        *args,
        **kwargs,
    ):
        ss = self.autorange_generator()
        iterations = ss.send(None)
        while True:
            try:
                iterations = ss.send(await bench_func(iterations, self.timer, *args, **kwargs))
            except StopIteration:
                return await func(*args, **kwargs)

    def to_bench_func(self, func, _globals=None):
        func_name = f"___bench_{func.__name__}"
        src = make_timeit_source(func_name, func)
        if self.verbose:
            logging.info(src)
        local_ns = {}
        exec(compile(src, "<timeit-src>", "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT), _globals, local_ns)
        return local_ns[func_name]

    def autorange_generator(self, *args, **kwargs):
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

    def print_bench(self, time, tabsize=20, args=[], kwargs={}):
        label = f"{self.label}{format_args(*args, **kwargs)}:"
        logging.info(f"{self.label:<{tabsize}}{metric(time, 's', skip_trailing_zeroes=False):>{8}} {format_ops(1/time):>{tabsize}}")


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
