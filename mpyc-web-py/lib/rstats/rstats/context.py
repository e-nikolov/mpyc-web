import asyncio
from contextlib import ContextDecorator
from typing import Any, Awaitable, Callable, ParamSpec, TypedDict, TypeGuard, TypeVar

try:
    import gc

    default_disable_gc = True
except ImportError:
    default_disable_gc = False


class GCManager(ContextDecorator):
    def __init__(self, disable_gc=default_disable_gc):
        # def __init__(self, func, _globals, iters, disable_gc=default_disable_gc):
        self.disable_gc = disable_gc
        self.gcold = gc.isenabled()
        # self.runnable = make_runnable(func, _globals)

    def __enter__(self):
        if self.disable_gc:
            self.gcold = gc.isenabled()
            gc.disable()

        # self.runnable = make_runnable()
        return self

    def __exit__(self, *exc):
        if self.disable_gc and self.gcold:
            gc.enable()
