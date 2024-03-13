import itertools
import math
import random
import sys
import time

from lib.rstats.rstats.bench import bench

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 1

range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide


l = None


@bench("assign")
def assign():
    for _ in range_fn(bench_input_size):
        x = 1


@bench("multiply")
def multiply():
    for _ in range_fn(bench_input_size):
        17 * 41


@bench("nothing", verbose=True)
def nothing():
    for _ in itertools.repeat(bench_input_size):
        pass


@bench("nothing_no_loop", verbose=True)
def nothing_no_loop(): ...


@bench("bigint_add")
def bigint_add():
    x = 1
    for _ in range_fn(bench_input_size):
        x += 2**600
    return x


@bench("bigint_mult")
def bigint_mult():
    x = 1
    for _ in range_fn(1000):
        x *= 2**600
    return x


@bench("bigints_old")
def bigint_old():
    for _ in range_fn(bench_input_size):
        2**60


@bench("randlist")
def randlist():
    return [random.randint(0, bench_input_size) for _ in range(bench_input_size)]


l = None


@bench("cpylist")
def cpylist():
    return l.copy()


@bench("cpylist2")
def cpylist2():
    return l[:]


@bench("sortlist")
def sortlist():
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
    for _ in range_fn(bench_input_size):
        fn()


@bench("itertools_repeat_no_loop")
def ittr_no_loop():
    itertools.repeat(None, bench_input_size)


@bench("itertools_repeat")
def ittr():
    for _ in range_fn(bench_input_size):
        itertools.repeat(None, bench_input_size)


@bench("range_fn_bench")
def range_fn_bench():
    for _ in range_fn(bench_input_size):
        range_fn(bench_input_size)


@bench("range_fn_bench_no_loop")
def range_fn_bench_no_loop():
    range_fn(bench_input_size)


@bench("ret")
def ret():
    pass


nothing_no_loop()
nothing()
callfunc()

assign()
multiply()
bigint_add()

bigint_mult()

bigint_old()
l = randlist()
sortlist()
fibonacci()
primes()
tryexcept()

# ittr()
# ittr_no_loop()
# range_fn_bench()
# range_fn_bench_no_loop()
