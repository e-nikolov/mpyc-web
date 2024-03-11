import inspect
import itertools
import logging
import random
import sys
import time

# import timeit

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 2


range_fn = range
# range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide


default_timer = time.time
default_time_diff = lambda a, b: a - b

l = None


def print(s):
    document.getElementById("output").innerHTML += s + "<br />"


from org.transcrypt.stubs.browser import __envir__, __pragma__

# try:
#     import gc
# except:
#     print("no gc")

# Provide waitAWhile for Transcrypt

__pragma__(
    "js",
    "{}",
    """
    
    var counter = 0;
    var queue = {};
    var channel = new MessageChannel();

    channel.port1.onmessage = function (event) {
        var id = event.data;
        var callback = queue[id];
        delete queue[id];
        callback();
    };

    const setImmediate = (callback) => {
        queue[++counter] = callback;
        channel.port2.postMessage(counter);
    }

    function scheduleCallback(callback, timeout) {
        if (timeout < 4) {
            setImmediate(callback)
        } else {
            setTimeout(callback, timeout);
        }
    }

    function waitAWhile (aTime, asio) {
      return new Promise (resolve => {
        scheduleCallback (() => {
          resolve (aTime);
        }, 1000 * aTime);
      });
    }
""",
)

__pragma__("skip")  # Compile time, needed because import is done compile time

import asyncio


def waitAWhile(aTime, asio):
    return asio.sleep(aTime)


__pragma__("noskip")


def timeit(func, iterations=bench_input_size, timer=default_timer, time_diff=default_time_diff):
    t1 = timer()
    res = func()
    for _ in range_fn(iterations - 1):
        func()
    timing = time_diff(timer(), t1)
    return timing, res


async def timeit_async(func, iterations=bench_input_size, timer=default_timer, time_diff=default_time_diff):
    t1 = timer()
    res = await func()
    for _ in range_fn(iterations - 1):
        await func()
    timing = time_diff(timer(), t1)
    return timing, res


def autorange(func):
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            time_taken, res = timeit(func, iterations)
            if time_taken >= bench_min_duration:
                return (round(iterations / time_taken, 0), res)
        i *= 10


async def autorange_async(func):
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            time_taken, res = await timeit_async(func, iterations)
            if time_taken >= bench_min_duration:
                return (round(iterations / time_taken, 0), res)
        i *= 10


def bench(name):
    def _bench(func):

        def wrapper(*args):
            maxOpS = 0
            res = None

            def handle():
                return func(*args)

            for _ in range(bench_best_of):
                ops, res = autorange(handle)
                maxOpS = max(maxOpS, ops)
            print_bench(name, maxOpS, *args)
            return res

        return wrapper

    return _bench


def bench_async(name):
    def _bench(func):
        async def wrapper(*args):
            maxOpS = 0
            res = None

            def handle():
                return func(*args)

            for _ in range(bench_best_of):
                ops, res = await autorange_async(handle)
                maxOpS = max(maxOpS, ops)

            print_bench(name, maxOpS, *args)
            return res

        return wrapper  # pyright: ignore

    return _bench  # pyright: ignore


def print_bench(name, t, *args):
    args_repr = [repr(arg) for arg in args]
    args_fmt = ", ".join(args_repr)
    print(f"{name}({args_fmt}): {t:,} ops/sec")


@bench("assign")
def assign(iters=bench_input_size):
    for _ in range_fn(iters):
        x = 1


@bench("multiply")
def multiply(iters=bench_input_size):
    a, b = 17, 41
    for _ in range_fn(iters):
        x = a * b


@bench("bigints")
def bigints(iters=bench_input_size):
    n = 600
    for _ in range_fn(iters):
        2**n


@bench("randlist")
def randlist(size=bench_input_size):
    return [random.randint(0, size) for _ in range(size)]


@bench("cpylist")
def cpylist() -> list[int]:
    return l[:]


@bench("sortlist")
def sortlist():
    return sorted(l[:])


@bench("sortlist2")
def sortlist2():
    return l[:].sort()


@bench("fibonacci")
def fibonacci(n=bench_input_size):
    if n < 2:
        return n
    a, b = 1, 2

    for _ in range_fn(n - 1):
        a, b = b, (a + b) % 100000
    return a


@bench("primes")
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


# pylint: disable-all


# loop = asyncio.get_event_loop()


# # For sync functions
# @bench("sync_function")
# def sync_function():
#     time.sleep(1)
#     print("Sync Function")


# @bench("async_sleep_0123")
# async def async_sleep_0123(a, b, c=4):
#     await asyncio.sleep(0.123)


@bench_async("async_nothing")
async def async_nothing():
    pass


# @bench("sync_nothing")
# def sync_nothing():
#     pass


@bench_async("async_sleep_0")
async def async_sleep_0():
    await waitAWhile(0)


# @bench("async_sleep_0001")
# async def async_sleep_0001():
#     await asyncio.sleep(0.001)


# @bench("async_sleep_0002")
# async def async_sleep_0002():
#     await asyncio.sleep(0.002)


# @bench("async_sleep_0004")
# async def async_sleep_0004():
#     await asyncio.sleep(0.004)


# @bench("sync_nothing")
# def add(a, b, c=4):
#     1 + 1


# @bench("add2")
# def add2(a, b, c=4):
#     a = 1
#     b = 2
#     c = a + b


# @bench("add3")
# def add3(a, b, c=4):
#     return a + b


# @bench("loopz")
# def loopz(a, b, c=4):
#     x = 1
#     for i in range(1000):
#         x += i
#     return x


async def main():
    await async_nothing()
    await async_sleep_0()


if __envir__.executor_name == __envir__.transpiler_name:
    await main()

else:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

#     # sync_sleep_0()

#     # await async_nothing()
#     # sync_nothing()
#     print("---done---")


assign()
multiply()
bigints()
l = randlist()
cpylist()
sortlist()
sortlist2()
fibonacci()
primes()
