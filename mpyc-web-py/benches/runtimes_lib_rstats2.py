import itertools
import math
import random
import sys
import time

from lib.rstats.rstats.bench_class_no_types import bench

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 12

range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide


@bench("assign")
def assign(iters=bench_input_size):
    for _ in itertools.repeat(None, iters):
        x = 1


@bench("multiply")
def multiply(iters=bench_input_size):
    for _ in itertools.repeat(None, iters):
        17 * 41


@bench("nothing")
def nothing(iters=bench_input_size):
    for _ in itertools.repeat(None, iters):
        pass


@bench("nothing_no_loop")
def nothing_no_loop(iters=bench_input_size): ...


@bench("bigint_add")
def bigint_add(iters=bench_input_size):
    x = 1
    for _ in itertools.repeat(None, iters):
        x += 2**600
    return x


@bench("bigint_mult")
def bigint_mult(iters=1000):
    x = 1
    for _ in itertools.repeat(None, iters):
        x *= 2**600
    return x


@bench("bigints_old")
def bigint_old(iters=bench_input_size):
    for _ in itertools.repeat(None, iters):
        2**60


@bench("randlist")
def randlist(size=bench_input_size):
    return [random.randint(0, size) for _ in itertools.repeat(None, size)]


l = None


@bench("sortlist", verbose=True)
def sortlist():
    print(len(l))
    return l.copy().sort()


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


@bench("tryexcept")
def tryexcept():
    for _ in range_fn(bench_input_size):
        try:
            raise Exception("test")
        except Exception as exc:
            pass


def fn(): ...


@bench("callfunc")
def callfunc():
    for _ in itertools.repeat(None, bench_input_size):
        fn()


@bench("itertools_repeat_no_loop")
def itertools_repeat_no_loop():
    itertools.repeat(None, bench_input_size)


@bench("itertools_repeat")
def itertools_repeat():
    for _ in itertools.repeat(None, bench_input_size):
        itertools.repeat(None, bench_input_size)


@bench("range_fn_bench")
def range_fn_bench():
    for _ in itertools.repeat(None, bench_input_size):
        range_fn(bench_input_size)


@bench("range_fn_bench_no_loop")
def range_fn_bench_no_loop():
    range_fn(bench_input_size)


@bench("ret")
def ret():
    return


# ret()
# callfunc()
# tryexcept()
import asyncio


@bench("sleep", verbose=True)
async def sleep():
    await asyncio.sleep(0.01)
    return 123


x = await sleep()

nothing()
nothing_no_loop()
# itertools_repeat_no_loop()
# itertools_repeat()
# range_fn_bench()
# range_fn_bench_no_loop()

# assign()
# multiply()
bigint_add()

# if not is_micropython():
bigint_mult()

bigint_old()
l = randlist()
print(f"{len(l)=}")
# cpylist()
# cpylist2()
sortlist()
fibonacci()
primes()
