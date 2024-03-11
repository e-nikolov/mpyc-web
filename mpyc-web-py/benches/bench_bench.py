import asyncio
import time

from lib.rstats.rstats.bench import bench


def fast_func():
    return 2 + 2


sfi = 0


@bench()
def time_time():
    time.time()


@bench()
def time_perf():
    time.perf_counter()


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


@bench()
def add(aaa, a=11):
    return 2 + 2


@bench(verbose=False)
def add3(fast=False):
    _ = 2 + 2
    if fast:
        return fast_func()

    return slow_func()


loop = asyncio.get_event_loop()


@bench()
def call_soon():
    loop.call_soon(fast_func)


csi = 0


@bench(verbose=False)
async def call_soon_async():
    global csi
    csi += 1

    # if csi % 1000000 == 0:
    #     print(csi)
    loop.call_soon(fast_func)


@bench()
async def sleep(n=0):
    await asyncio.sleep(n)


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


def other():
    pass


import itertools

it = itertools.repeat(None, 10000000)
it2 = itertools.repeat(None, 10000000)
it3 = itertools.repeat(None, 10000000)


@bench(best_of=1)
def test():
    i = 0
    print(f"start {i=}")
    print(f"start {it=}")
    print(f"start {it2=}")
    print(f"start {it3=}")
    for _ in it:
        for _ in it2:
            for _ in it3:
                i += 1
                pass
    print(f"end {i=}")
    print(f"end {it=}")
    print(f"end {it2=}")
    print(f"end {it3=}")


async def main():
    test()
    await sleep(0)
    await call_soon_async()
    nothing()
    time_time()
    time_perf()
    add(31)
    add3(False)
    add3(True)
    add2()
    call_soon()


asyncio.get_event_loop().run_until_complete(main())

# pprint("t" * 0)
