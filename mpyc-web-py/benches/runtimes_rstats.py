import itertools
import random
import sys
import time

from rstats import bench

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 3


range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide


@bench
def assign(iters=bench_input_size):
    for _ in range_fn(iters):
        x = 1


@bench
def multiply(iters=bench_input_size):
    a, b = 17, 41
    for _ in range_fn(iters):
        x = a * b


@bench
def nothing(iters=bench_input_size):
    for _ in range_fn(iters):
        pass


@bench
def nothing2(iters=bench_input_size):
    pass


@bench
def bigints(iters=bench_input_size):
    n = 60
    for _ in range_fn(iters):
        2**n


@bench
def randlist(size=bench_input_size):
    return [random.randint(0, size) for _ in range(size)]


l = None


@bench
def cpylist():
    return l.copy()


@bench
def cpylist2():
    return l[:]


@bench
def sortlist():
    return l.copy().sort()


@bench
def fibonacci(n=bench_input_size):
    if n < 2:
        return n
    a, b = 1, 2

    for _ in range_fn(n - 1):
        a, b = b, (a + b) % 100000
    return a


@bench
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


nothing()
nothing2()
assign()
multiply()
bigints()
_, l = randlist()
cpylist()
cpylist2()
sortlist()
fibonacci()
primes()
