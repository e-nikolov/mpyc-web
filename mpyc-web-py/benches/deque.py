import collections
import logging

from lib.rstats.rstats import bench

bench_input_size = 100_000

_queue: collections.deque = collections.deque()


@bench()
def deque_append(queue: collections.deque = _queue):
    queue.append(1)


@bench()
def deque_appendleft(queue: collections.deque = _queue):
    _queue.appendleft(1)


@bench()
def deque_append_popleft(queue: collections.deque = _queue):
    _queue.append(1)
    _queue.popleft()


@bench()
def deque_appendleft_popLeft(queue: collections.deque = _queue):
    _queue.appendleft(1)
    _queue.popleft()


@bench()
def deque_append_pop(queue: collections.deque = _queue):
    _queue.append(1)
    _queue.pop()


@bench()
def deque_appendleft_pop(queue: collections.deque = _queue):
    _queue.appendleft(1)
    _queue.pop()


@bench()
def nothing():
    pass


@bench()
def add():
    1 + 1


def setup_queue():
    q = collections.deque()
    for i in range(bench_input_size):
        q.append(i)
    return q


def main():
    nothing()
    add()

    deque_append()
    deque_appendleft()
    deque_append_popleft(setup_queue())
    deque_appendleft_popLeft(setup_queue())
    deque_append_pop(setup_queue())
    deque_appendleft_pop(setup_queue())
    logging.info("---done---")


main()
