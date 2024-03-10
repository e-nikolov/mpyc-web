import asyncio
from functools import wraps

from lib.rstats.rstats.bench_timeit3 import bench

# from lib.rstats.rstats.bench2 import bench


def dec(a, b, c):
    def decorator(fn):
        @wraps(fn)
        def wrapper2(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper2

    return decorator


def fast_func():
    return 2 + 2


sfi = 0


def slow_func():
    global sfi
    for _ in range(100000):
        _ = 2 + 2
    sfi += 1
    if sfi % 1000 == 0:
        print("slow_func done", sfi)
    return 2 + 2


@bench()
def nothing():
    pass


@bench()
def pprint(msg="test"):
    print(msg)


@dec(1, 2, 3)
@bench()
def add(aaa, a=11):
    return 2 + 2


@bench(verbose=False)
@dec(1, 2, 3)
def add3(fast=False):
    _ = 2 + 2
    if fast:
        return fast_func()

    return slow_func()


loop = asyncio.get_event_loop()


@dec(1, 2, 3)
@bench()
def call_soon():
    loop.call_soon(fast_func)


csi = 0


@dec(1, 2, 3)
@bench(verbose=False)
async def call_soon_async():
    global csi
    csi += 1

    # if csi % 1000000 == 0:
    #     print(csi)
    loop.call_soon(fast_func)


@dec(1, 2, 3)
@bench()
async def sleep(n=0):
    await asyncio.sleep(n)


@dec(1, 2, 3)
@bench()
def add2():
    return add_rec()


x = 0


def add_rec():
    global x
    x += 1
    if x > 100:
        x = 3
        return 17
    2 + 2

    return add_rec()


async def main():
    await call_soon_async()
    await sleep(0)


asyncio.get_event_loop().run_until_complete(main())

# pprint("t" * 0)
nothing()
add(31)
add3(False)
add3(True)
add2()
call_soon()
