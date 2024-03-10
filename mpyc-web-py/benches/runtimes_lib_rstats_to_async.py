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

from rstats.bench_to_async import bench

# pylint: disable-all


if len(logging.root.handlers) == 0:
    logging.basicConfig(level=logging.INFO)

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 3


range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide


@bench()
def time_time(iters=bench_input_size):
    time.time()


@bench()
def time_ns(iters=bench_input_size):
    time.time_ns()


@bench()
def time_monotonic(iters=bench_input_size):
    time.monotonic()


@bench()
def time_monotonic_ns(iters=bench_input_size):
    time.monotonic_ns()


@bench()
def time_perf(iters=bench_input_size):
    time.perf_counter()


@bench()
def time_perf_ns(iters=bench_input_size):
    time.perf_counter_ns()


@bench()
def nothing_pass(iters=bench_input_size):
    pass


@bench()
def nothing_range_fn(iters=bench_input_size):
    for _ in range_fn(iters):
        pass


@bench()
def nothing_repeat(iters=bench_input_size):
    for _ in itertools.repeat(None, iters):
        pass


@bench()
def nothing_range(iters=bench_input_size):
    for _ in range(iters):
        pass


@bench()
def assign(iters=bench_input_size):
    for _ in range_fn(iters):
        x = 1


@bench()
def multiply(iters=bench_input_size):
    a, b = 17, 41
    for _ in range_fn(iters):
        x = a * b


@bench()
def bigints(iters=bench_input_size):
    n = 60
    for _ in range_fn(iters):
        2**n


@bench()
def randlist(size=bench_input_size):
    return [random.randint(0, size) for _ in range(size)]


l = None


@bench()
def cpylist():
    return l.copy()


@bench():# -> tuple[int, Any] | None
def cpylist2():
    return l[:]


@bench()
def sortlist():
    return l.copy().sort()


@bench()
def fibonacci(n=bench_input_size):
    if n < 2:
        return n
    a, b = 1, 2

    for _ in range_fn(n - 1):
        a, b = b, (a + b) % 100000
    return a


@bench()
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


@bench()
def add():
    1 + 1


@bench()
def padd():
    pass


loop = asyncio.get_event_loop()


@bench()
async def call_soon_async():
    loop.call_soon(lambda: None)


@bench()
def call_soon():
    loop.call_soon(lambda: None)


@bench()
async def sleep():
    await asyncio.sleep(0)


async def main():
    global l
    await sleep()
    await call_soon()
    await call_soon_async()
    await add()
    await padd()
    await nothing_pass()
    await nothing_range_fn()
    await nothing_repeat()
    await nothing_range()
    await time_time()
    await time_ns()
    await time_monotonic()
    await time_monotonic_ns()
    await time_perf()
    await time_perf_ns()
    await assign()
    await multiply()
    l = await randlist()
    await cpylist()
    await cpylist2()
    await sortlist()
    await fibonacci()
    await primes()


loop.run_until_complete(main())
