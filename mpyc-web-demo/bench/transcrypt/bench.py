from org.transcrypt.stubs.browser import __envir__, __pragma__

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

    function sleep (aTime, asio) {
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


def sleep(ms, asio):
    return asio.sleep(ms)


__pragma__("noskip")


def display(s):
    document.getElementById("output").innerHTML += s + "<br />"


import math
import random
import time

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 1


default_timer = time.time
default_time_diff = lambda a, b: a - b

l = None


def timeit(func, iterations=bench_input_size, timer=default_timer, time_diff=default_time_diff, args=[]):
    t1 = timer()
    res = func()
    for _ in range(iterations - 1):
        func()
    timing = time_diff(timer(), t1)
    return timing, res


async def timeit_async(func, iterations=bench_input_size, timer=default_timer, time_diff=default_time_diff, args=[]):
    t1 = timer()
    res = await func()
    for _ in range(iterations - 1):
        await func()
    timing = time_diff(timer(), t1)
    return timing, res


def autorange(func, args=[]):
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            time_taken, res = timeit(func, iterations, args=args)
            if time_taken >= bench_min_duration:
                return time_taken / iterations, res
        i *= 10


async def autorange_async(func, *args):
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            time_taken, res = await timeit_async(func, iterations, args=args)
            if time_taken >= bench_min_duration:
                return time_taken / iterations, res
        i *= 10


def bench(name):
    def _bench(func):

        def wrapper(*args):
            min_time_taken = float("inf")
            res = None

            for _ in range(bench_best_of):
                time_taken, res = autorange(func, args=args)
                min_time_taken = min(min_time_taken, time_taken)
            print_bench(name, min_time_taken, args=args)
            return res

        return wrapper

    return _bench


def bench_async(name):
    def _bench(func):
        async def wrapper(*args):
            min_time_taken = float("inf")
            res = None
            for _ in range(bench_best_of):
                time_taken, res = await autorange_async(func)
                min_time_taken = min(min_time_taken, time_taken)

            print_bench(name, min_time_taken, *args)
            return res

        return wrapper  # pyright: ignore

    return _bench  # pyright: ignore


def format_ms(ops: float) -> str:
    ms = 1000 / ops
    return f"{ops:_} ms"


def _repr(arg):
    try:
        l = len(arg)
        if l > 10:
            return f"{type(arg).__name__}[{l}]"
        return repr(arg)
    except:
        return repr(arg)


def format_args(*args):
    args_repr = [_repr(arg) for arg in args]
    args_fmt = ", ".join(args_repr)
    if args_fmt != "":
        args_fmt = f"({args_fmt})"
    return args_fmt


def metric(value: float, unit: str = "", precision: int = 3) -> str:
    if not math.isfinite(value):
        return _format_not_finite(value)  # type: ignore # pylint: disable=import-error, no-name-in-module, no-member, protected-access
    exponent = int(math.floor(math.log10(abs(value)))) if value != 0 else 0

    value /= 10 ** (exponent // 3 * 3)
    if exponent >= 3:
        ordinal_ = "kMGTPEZYRQ"[exponent // 3 - 1]
    elif exponent < 0:
        ordinal_ = "mμnpfazyrq"[(-exponent - 1) // 3]
    else:
        ordinal_ = ""

    precision = max(0, precision - (exponent % 3) - 1)
    value = round(value, precision)
    value_ = format(value, ".%if" % precision)
    if not (unit or ordinal_) or unit in ("°", "′", "″"):
        space = ""
    else:
        space = " "

    return f"{value_}{space}{ordinal_}{unit}"


def f(x, unit="ns"):
    x = round(x, 1)
    return f"{x:12,.1f} {unit}"


def format_num(ops: float, unit="") -> str:
    if ops < 10:
        ops = round(ops, 2)
    else:
        ops = round(ops)

    int_part, float_part = f"{ops}".split(".")
    # int_part = int_part[::-1]

    res = ""

    i = 0
    for c in reversed(list(int_part)):
        if i % 3 == 0 and i > 0:
            res += ","
        res += c

        i += 1

    # res = res[::-1]
    if float_part:
        return f"{res}.{float_part} {unit}"
    return f"{''.join(reversed(list(res)))} {unit}"


# def format_ops(ops: float) -> str:
#     return f"{round(ops):,} ops/s"


def align_left(value, tabsize=25):
    spaces = ""
    for _ in range(max(0, tabsize - len(value))):
        spaces += " "
    if spaces != "":
        return f"{value}{spaces}"
    return value


def align_right(value, tabsize=25):
    spaces = ""
    for _ in range(max(0, tabsize - len(value))):
        spaces += " "
    if spaces != "":
        return f"{spaces}{value}"
    return value


def print_bench(label, time, tabsize=25, args=[]):
    label = f"{label}{format_args(*args)}:"
    label = align_left(label)

    ms_str = align_right(f"{format_num(1_000 * time, 'ms')}", 10)
    ops_str = align_right(f"{format_num(1/time, 'ops/s')}", tabsize)
    display(f"{label}\t{ms_str}\t{ops_str}")
    # print(f2(ops, "s"))


# def print_bench(label, ops, tabsize=20, args=[], kwargs={}):
#     label = f"{label}{format_args(*args, **kwargs)}:"
#     display(f"{label:<{tabsize}}{metric(1 / ops, 's'):>{6}} {format_ops(ops):>{tabsize}}")


@bench("assign")
def assign(iters=bench_input_size):
    for _ in range(iters):
        x = 1


@bench("multiply")
def multiply(iters=bench_input_size):
    for _ in range(iters):
        17 * 47


@bench("bigint_add")
def bigint_add(iters=bench_input_size):
    x = 1
    for _ in range(iters):
        x += 2**600
    return x


@bench("bigint_mult")
# def bigint_mult(iters=1000):
def bigint_mult(iters=bench_input_size):
    x = 1
    for _ in range(iters):
        x *= 2**600
    return x


@bench("randlist")
def randlist(size=bench_input_size):
    return [random.randint(0, size) for _ in range(size)]


def _randlist(size=bench_input_size):
    return [random.randint(0, size) for _ in range(size)]


l = _randlist()


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

    for _ in range(n - 1):
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
    for _ in range(bench_input_size):
        try:
            raise Exception("test")
        except Exception as exc:
            pass


def fn():
    pass


@bench("callfunc")
def callfunc():
    for _ in range(bench_input_size):
        fn()


@bench("ret")
def ret():
    return True


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
    await sleep(0)


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


@bench("nothing")
def nothing():
    for _ in range(bench_input_size):
        pass


class CancelledException(Exception):
    pass


def set_best_of(best_of):
    global bench_best_of
    bench_best_of = best_of


def set_min_duration(min_duration):
    global bench_min_duration
    bench_min_duration = min_duration


class Bench:
    cancelled = False

    def cancel(self):
        self.cancelled = True

    async def _run(self, fn):
        if self.cancelled:
            raise CancelledException
        fn()
        await sleep(0.1)

    async def run(self):
        try:
            await self._run(randlist)
            await self._run(nothing)
            await self._run(callfunc)
            await self._run(bigint_add)
            await self._run(bigint_mult)
            await self._run(cpylist)
            await self._run(sortlist)
            await self._run(sortlist2)
            await self._run(fibonacci)
            await self._run(primes)
            await self._run(tryexcept)
        except Exception as e:
            console.warn("exception", e)
            pass
        except:
            console.warn("unknown exception")

    # ret()

    # await async_nothing()
    # await async_sleep_0()


# if __envir__.executor_name == __envir__.transpiler_name:
#     await main()

# else:
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())

#     # sync_sleep_0()

#     # await async_nothing()
#     # sync_nothing()
#     print("---done---")
