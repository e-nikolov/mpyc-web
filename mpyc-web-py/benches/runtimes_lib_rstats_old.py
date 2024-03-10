import asyncio
import itertools
import random
import sys
import time
from typing import overload

from lib.rstats.rstats.bench_old import bench

# from rstats import bench, statsa
from lib.stats import stats

bench_input_size = 100000
bench_min_duration = 0.2
bench_best_of = 3


loop = asyncio.get_event_loop()
range_fn = lambda iters: itertools.repeat(None, iters)  # Pyodide
# range_fn = lambda iters: range(iters)  # Pyodide


def dec(a, b, c):
    def decorator(fn):
        def wrapper2(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper2

    return decorator


# @dec(1, 2, 3)
@bench(1, 2, 3)
def add():
    return 1 + 1


add()
