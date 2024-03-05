import itertools
import time

default_iterations = 1000000
default_timer = time.time
min_bench_duration = 0.2


def timeit(func, iterations=default_iterations, timer=default_timer):
    it = itertools.repeat(None, iterations - 1)
    t1 = timer()
    res = func()
    for _ in it:
        func()
    timing = timer() - t1
    return timing, res


def autorange(func):
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            time_taken, res = timeit(func, iterations)
            if time_taken >= min_bench_duration:
                return (round(iterations / time_taken, 2), res)
        i *= 10


def bench(func):
    def wrapper(*args, **kwargs):
        maxOpS = 0
        res = None

        def handle():
            return func(*args, **kwargs)

        for _ in range(3):
            ops, res = autorange(handle)
            maxOpS = max(maxOpS, ops)

        print_bench(func.__name__, maxOpS, *args, **kwargs)
        return maxOpS, res

    return wrapper


def print_bench(name, t, *args, **kwargs):
    args_repr = [repr(arg) for arg in args]
    kwargs_repr = [f"{key}={repr(value)}" for key, value in kwargs.items()]
    args_fmt = ", ".join(args_repr + kwargs_repr)
    print(f"{name}({args_fmt}): {t:,} ops/sec")


@bench
def assign(iters=default_iterations):
    x = 0
    for i in range(iters):
        x = i


@bench
def add(iters=default_iterations):
    x = 0
    for i in range(iters):
        x = x + i


@bench
def mod(iters=default_iterations):
    x = 123456
    for i in range(iters):
        x % 12345


@bench
def big_int(iters=default_iterations):
    n = 60
    for i in range(iters):
        2**n


@bench
def mult(iters=default_iterations):
    x = 0
    for i in range(iters):
        x *= i


@bench
def create_func(iters=default_iterations):
    for i in range(iters):

        def ff(x):
            return x

    return ff


@bench
def append_list(iters=default_iterations):
    t = []
    i = 0
    while i < iters:
        t.append(i)
        i += 1


@bench
def add_dict(iters=default_iterations):
    d = {}

    for i in range(iters):
        d[i] = i


@bench
def build_dict(iters=default_iterations):
    for i in range(iters):
        a = {0: 0, "a": "a"}


@bench
def build_list(iters=default_iterations):
    for i in range(iters):
        a = [1, 2, 3]


def f(x):
    return x


@bench
def function_call(iters=default_iterations):

    for i in range(iters):
        f(i)


@bench
def str_of_int(iters=default_iterations):
    for i in range(iters):
        str(i)


# @bench
def set_dict_item(iters=default_iterations):
    a = {0: 0}
    for i in range(iters):
        a[0] = i


@bench
def hash_str(iters=default_iterations):
    for i in range(iters):
        hash("abcdef")


# @bench
def primes(n=default_iterations):
    if n == 2:
        return [2]
    elif n < 2:
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


from mpyc import finfields, gfpx, thresha


@bench
def fields():
    f2 = finfields.GF(2)
    f256 = finfields.GF(gfpx.GFpX(2)(283))

    for field in (f2, f256):
        t = 0
        m = 1
        a = [field(0), field(1)]
        shares = thresha.random_split(field, a, t, m)
        b = thresha.recombine(field, [(j + 1, shares[j]) for j in range(len(shares))])
        b = thresha.recombine(field, [(j + 1, shares[j]) for j in range(len(shares))], [0])[0]


fields()

# assign()
# add()
# mod()
# mult()
# big_int()
# str_of_int()
# function_call()
# hash_str()
# create_func()
# append_list()
# add_dict()
# build_dict()
# create_function_single_pos_arg()
# set_dict_item()
