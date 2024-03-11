import gc
import itertools
import random
import sys
import time

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 3


def is_brython():
    return "Brython" in str(sys.version)


def is_skulpt():
    return "Skulpt" in str(sys.version)


def is_micropython():
    return "MicroPython" in str(sys.version)


def is_rustpython():
    return "rustc" in str(sys.version)


if is_micropython():
    import js

    def print(s):
        js.document.currentScript.target.innerHTML += s + "<br />"


if is_brython() or is_skulpt() or is_micropython():
    range_fn = range
else:
    range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide

if hasattr(time, "ticks_ms"):
    default_timer = time.ticks_ms
    default_time_diff = lambda a, b: time.ticks_diff(a, b) / 1000.0

elif hasattr(time, "time"):
    default_timer = time.time
    default_time_diff = lambda a, b: a - b


def timeit(func, iterations=bench_input_size, timer=default_timer, time_diff=default_time_diff):
    t1 = timer()
    res = func()
    for _ in range_fn(iterations - 1):
        func()
    timing = time_diff(timer(), t1)
    return timing, res


def autorange(func):
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            time_taken, res = timeit(func, iterations)
            if time_taken >= bench_min_duration:
                return (round(iterations / time_taken), res)
        i *= 10


def bench():
    def _bench(func):
        def wrapper(*args, **kwargs):
            maxOpS = 0
            res = None

            def handle():
                return func(*args, **kwargs)

            for _ in range(bench_best_of):
                ops, res = autorange(handle)
                maxOpS = max(maxOpS, ops)

            print_bench(func.__name__, maxOpS, *args, **kwargs)
            return res

        return wrapper

    return _bench


def print_bench(name, t, *args, **kwargs):
    args_repr = [repr(arg) for arg in args]
    kwargs_repr = [f"{key}={repr(value)}" for key, value in kwargs.items()]
    args_fmt = ", ".join(args_repr + kwargs_repr)
    print(f"{name}({args_fmt}): {t:,} ops/sec")


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
def nothing(iters=bench_input_size):
    for _ in range_fn(iters):
        pass


@bench()
def nothing2(iters=bench_input_size):
    pass


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


@bench()
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


nothing()
nothing2()
assign()
multiply()
bigints()
l = randlist()
cpylist()
cpylist2()
sortlist()
fibonacci()
primes()
