import asyncio
import collections
import gc
import inspect
import itertools
import logging
import random
import sys
import time
import timeit
from contextlib import ContextDecorator, contextmanager
from functools import partial, reduce, wraps
from inspect import isawaitable, isfunction
from types import FrameType
from typing import Any, Awaitable, Callable, ParamSpec, TypeGuard, TypeVar, overload

# pylint: disable-all
if len(logging.root.handlers) == 0:
    logging.basicConfig(level=logging.DEBUG)


bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 3


range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide


def time_time(iters=bench_input_size):
    time.time()


def time_ns(iters=bench_input_size):
    time.time_ns()


def time_monotonic(iters=bench_input_size):
    time.monotonic()


def time_monotonic_ns(iters=bench_input_size):
    time.monotonic_ns()


def time_perf(iters=bench_input_size):
    time.perf_counter()


def time_perf_ns(iters=bench_input_size):
    time.perf_counter_ns()


def nothing_pass(iters=bench_input_size):
    pass


def nothing_range_fn(iters=bench_input_size):
    for _ in range_fn(iters):
        pass


def nothing_repeat(iters=bench_input_size):
    for _ in itertools.repeat(None, iters):
        pass


def nothing_range(iters=bench_input_size):
    for _ in range(iters):
        pass


def assign(iters=bench_input_size):
    for _ in range_fn(iters):
        x = 1


def multiply(iters=bench_input_size):
    a, b = 17, 41
    for _ in range_fn(iters):
        x = a * b


def bigints(iters=bench_input_size):
    n = 60
    for _ in range_fn(iters):
        2**n


def randlist(size=bench_input_size):
    return [random.randint(0, size) for _ in range(size)]


l = None


def cpylist():
    return l.copy()


def add():
    1 + 1


def padd():
    pass


def cpylist2():
    return l[:]


def sortlist():
    return l.copy().sort()


def fibonacci(n=bench_input_size):
    if n < 2:
        return n
    a, b = 1, 2

    for _ in range_fn(n - 1):
        a, b = b, (a + b) % 100000
    return a


def primes(n=bench_input_size):
    if n == 2:
        return [2]
    if n < 2:
        return []
    s = list(range(3, n + 1, 2))
    mroot = n**0.5
    half = (n + 1) // 2 - 1
    i = 0
    m = 3
    while m <= mroot:
        if s[i]:
            j = (m * m - 3) // 2
            s[j] = 0
            while j < half:
                s[j] = 0
                j += m
        i = i + 1
        m = 2 * i + 3
    return [2] + [x for x in s if x]


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


def bench(func):
    ite, tt = timeit.Timer(func, globals=globals()).autorange()
    ops = ite / tt

    label = ""
    if hasattr(func, "__name__"):
        label = func.__name__
    else:
        label = func

    print_bench(label, ops)


loop = asyncio.get_event_loop()


async def call_soon_async():
    loop.call_soon(lambda: None)


def call_soon():
    loop.call_soon(lambda: None)


async def sleep():
    await asyncio.sleep(0)


yy = 123

bench("yy + 3")


async def main():
    global l
    bench("")
    bench("pass")
    bench("1+1")
    bench("1")
    bench("x = 3 * 3")
    bench("x = 3 * 3")
    bench("x = 3 * 3")
    bench(call_soon)
    # bench(call_soon_async)
    # bench(sleep)
    bench(add)
    bench(padd)
    bench(nothing_pass)
    bench(nothing_range_fn)
    bench(nothing_repeat)
    bench(nothing_range)
    bench(time_time)
    bench(time_ns)
    bench(time_monotonic)
    bench(time_monotonic_ns)
    bench(time_perf)
    bench(time_perf_ns)
    bench(assign)
    bench(multiply)
    bench(bigints)
    bench(randlist)
    l = randlist()
    bench(cpylist)
    bench(cpylist2)
    bench(sortlist)
    bench(fibonacci)
    bench(primes)


loop.run_until_complete(main())
