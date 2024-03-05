import itertools
import time

async_run = None
import sys

if "browser" in sys.modules:
    aio = __import__("browser.aio").aio
    print("detected aio")
    async_sleep = aio.sleep
    async_run = aio.run

else:
    try:
        import asyncio

        print("detected asyncio")
        async_run = asyncio.get_event_loop().run_until_complete
        async_sleep = asyncio.sleep
    except ImportError:
        print("No async support")

default_iterations = 1000000
default_repeat = 5
default_timer = time.time


async def _timeit_async(func, iterations=default_iterations, timer=default_timer):
    it = itertools.repeat(None, iterations - 1)
    t1 = timer()
    res = await func()
    for _ in it:
        await func()
    timing = timer() - t1
    return timing, res


async def autorange_async(func):
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            time_taken, res = await _timeit_async(func, iterations)
            if time_taken >= 0.2:
                return (round(iterations / time_taken, 2), res)
        i *= 10


def bench(name):
    def _bench(func):
        def bench_async(func):
            async def wrapper(*args, **kwargs):
                maxOpS = 0
                res = None

                def handle():
                    return func(*args, **kwargs)

                for _ in range(3):
                    ops, res = await autorange_async(handle)
                    maxOpS = max(maxOpS, ops)

                print_bench(name, maxOpS, res, *args, **kwargs)
                return maxOpS, res

            return wrapper  # pyright: ignore

        return bench_async(func)

    return _bench


def print_bench(name, t, res, *args, **kwargs):
    if name == "<lambda>":
        name = ""
    args_repr = [repr(arg) for arg in args]
    kwargs_repr = [f"{key}={repr(value)}" for key, value in kwargs.items()]
    args_fmt = ", ".join(args_repr + kwargs_repr)
    print(f"{name}({args_fmt}): {t:,} ops/sec")
    print(f"res: {res}")


@bench("sleep")
async def sleep(n):
    await async_sleep(n)


@bench("add")
async def add(n):
    x = 0
    for i in range(n):
        x += i
    return x


async def main():
    await add(10)
    await sleep(0)


async_run(main())
