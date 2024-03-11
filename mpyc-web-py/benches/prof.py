import asyncio

from lib.rstats.rstats.prof import prof

loop = asyncio.get_event_loop()
from lib.rstats.rstats.bench import bench


@bench()
def nothing():
    pass


# @bench(min_duration=15, best_of=1, verbose=True)
@bench(verbose=True)
def call_soon():

    def fast_func():
        return 2 + 2

    asyncio.get_event_loop().call_soon(fast_func)


@bench(min_duration=15, best_of=1)
async def sleep(n=0):
    await asyncio.sleep(n)


def main():
    call_soon()
    # await sleep(0)
    # nothing()


# prof(main)
