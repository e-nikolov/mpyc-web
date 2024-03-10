# pylint: disable-all

import asyncio
import collections
import gc
import inspect
import itertools
import logging
import sys
import time
import timeit
from contextlib import ContextDecorator, contextmanager
from functools import partial, reduce, wraps
from inspect import isawaitable, isfunction
from types import FrameType
from typing import Any, Awaitable, Callable, ParamSpec, TypeGuard, TypeVar, overload

type AsyncCallable[**P, R] = Callable[P, Awaitable[R]]
type MaybeAsyncCallable[**P, R] = AsyncCallable[P, R] | Callable[P, R]

if len(logging.root.handlers) == 0:
    logging.basicConfig(level=logging.INFO)
import gc
import itertools
import sys
import time

__all__ = ["Timer", "timeit", "repeat", "default_timer"]

dummy_src_name = "<timeit-src>"
default_number = 1000000
default_repeat = 5
default_timer = time.perf_counter

_globals = globals

# Don't change the indentation of the template; the reindent() calls
# in Timer.__init__() depend on setup being indented 4 spaces and stmt
# being indented 8 spaces.
template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        {stmt}
        pass
    _t1 = _timer()
    return _t1 - _t0
"""


def reindent(src, indent):
    """Helper to reindent a multi-line statement."""
    return src.replace("\n", "\n" + " " * indent)


class Timer:
    def __init__(self, stmt="pass", setup="pass", timer=default_timer, globals=None):
        self.timer = timer
        local_ns = {}
        global_ns = _globals() if globals is None else globals
        init = ""
        if isinstance(setup, str):
            # Check that the code can be compiled outside a function
            compile(setup, dummy_src_name, "exec")
            stmtprefix = setup + "\n"
            setup = reindent(setup, 4)
        elif callable(setup):
            local_ns["_setup"] = setup
            init += ", _setup=_setup"
            stmtprefix = ""
            setup = "_setup()"
        else:
            raise ValueError("setup is neither a string nor callable")
        if isinstance(stmt, str):
            # Check that the code can be compiled outside a function
            compile(stmtprefix + stmt, dummy_src_name, "exec")
            stmt = reindent(stmt, 8)
        elif callable(stmt):
            local_ns["_stmt"] = stmt
            init += ", _stmt=_stmt"
            stmt = "_stmt()"
        else:
            raise ValueError("stmt is neither a string nor callable")
        src = template.format(stmt=stmt, setup=setup, init=init)
        self.src = src  # Save for traceback display
        code = compile(src, dummy_src_name, "exec")
        exec(code, global_ns, local_ns)
        self.inner = local_ns["inner"]

    def print_exc(self, file=None):
        import linecache
        import traceback

        if self.src is not None:
            linecache.cache[dummy_src_name] = (len(self.src), None, self.src.split("\n"), dummy_src_name)
        # else the source is already stored somewhere else

        traceback.print_exc(file=file)

    def timeit(self, number=default_number):
        it = itertools.repeat(None, number)
        gcold = gc.isenabled()
        gc.disable()
        try:
            timing = self.inner(it, self.timer)
        finally:
            if gcold:
                gc.enable()
        return timing

    def repeat(self, repeat=default_repeat, number=default_number):
        r = []
        for i in range(repeat):
            t = self.timeit(number)
            r.append(t)
        return r

    def autorange(self, callback=None):
        for iterations in autorange_generator():
            time_taken = self.timeit(iterations)
            if time_taken >= 0.2:
                return (iterations, time_taken)


def autorange_generator():
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            yield iterations
        i *= 10


def timeit(stmt="pass", setup="pass", timer=default_timer, number=default_number, globals=None):
    """Convenience function to create Timer object and call timeit method."""
    return Timer(stmt, setup, timer, globals).timeit(number)


def repeat(stmt="pass", setup="pass", timer=default_timer, repeat=default_repeat, number=default_number, globals=None):
    """Convenience function to create Timer object and call repeat method."""
    return Timer(stmt, setup, timer, globals).repeat(repeat, number)


def format_ops(ops: float) -> str:
    return f"{round(ops):,} ops/sec"


def label_from_frame(frame: FrameType):
    f = frame.f_back

    if f is not None:
        func_name = f"{f.f_code.co_name}"
        if func_name == "<module>" or func_name == "<lambda>":
            func_name = ""
        else:
            func_name = f":{func_name}"

        return f"{f.f_code.co_filename}:{f.f_lineno}{func_name}"


class bench[**P, R](ContextDecorator):
    def __init__(
        self,
        label: str | None = None,
    ):
        self.label = label
        self.func: Callable | None = None
        self.args = []
        self.kwargs = {}

        self.ops = 0.0

    def _recreate_cm(self):
        """Return a recreated instance of self.

        Allows an otherwise one-shot context manager like
        _GeneratorContextManager to support use as
        a decorator via implicit recreation.

        This is a private interface just for _GeneratorContextManager.
        See issue #11647 for details.
        """
        return self

    def __call__(self, func: MaybeAsyncCallable[P, R]):
        self.label = self.label or func.__name__
        self.func = func

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs):
            self.args = args
            self.kwargs = kwargs
            with self._recreate_cm():
                ite, tt = Timer(func).autorange()
                self.ops = ite / tt
                return func()

        return wrapper

    def __enter__(self):
        self.label = self.label or label_from_frame(sys._getframe())
        return self

    def __exit__(self, *exc):
        print_bench(self.label or "default", self.ops, *self.args, **self.kwargs)
        self.ops = 0.0


def _repr(arg):
    if isinstance(arg, list | dict | tuple | set | collections.deque):
        return f"{type(arg).__name__}[{len(arg)}]"
    else:
        return repr(arg)


def format_args(*args, **kwargs):
    args_repr = [_repr(arg) for arg in args]
    kwargs_repr = [f"{key}={repr(value)}" for key, value in kwargs.items()]
    args_fmt = ", ".join(args_repr + kwargs_repr)
    if args_fmt != "":
        args_fmt = f"({args_fmt})"
    return args_fmt


def print_bench(label: str, ops: float, *args, **kwargs):
    logging.info(f"{label}{format_args(*args, **kwargs)}: {format_ops(ops)}")
