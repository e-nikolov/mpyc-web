def print(s):
    document.getElementById("output").innerHTML += s + "<br />"


import itertools
import random
import time

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 2


range_fn = range
# range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide


default_timer = time.time
default_time_diff = lambda a, b: a - b

l = None


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


assign()
multiply()
bigints()
l = randlist()
cpylist()
sortlist()
sortlist2()
fibonacci()
primes()
