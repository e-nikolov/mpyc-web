# pylint: disable-all

import ast
import asyncio
import gc
import inspect
import itertools
import logging
import sys
import textwrap
import time
from contextlib import ContextDecorator
from functools import partial, wraps
from types import FrameType
from typing import Any, Awaitable, Callable, Concatenate, Coroutine, Iterable, Iterator, ParamSpec, Sized, TypeGuard, TypeVar, Union, overload

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

AsyncCallable = Callable[P, Awaitable[R]]
MaybeAsyncCallable = AsyncCallable[P, R] | Callable[P, R]


def isasynccallable(func: MaybeAsyncCallable[P, R]) -> TypeGuard[AsyncCallable[P, R]]:
    return asyncio.iscoroutinefunction(func)


def isnotasynccallable(func: MaybeAsyncCallable[P, R]) -> TypeGuard[Callable[P, R]]:
    return not asyncio.iscoroutinefunction(func)


default_iterations = 1000000
default_best_of = 2
default_min_duration = 0.2
default_timer = time.perf_counter


class bench:
    func: Callable

    def __init__(self, label: str | None = None, best_of=default_best_of, min_duration=default_min_duration, timer=default_timer, verbose=False, _globals=None):
        self.label = label
        self.best_of = best_of
        self.min_duration = min_duration
        self.timer = timer
        self.args = []
        self.kwargs = {}
        self.verbose = verbose
        self._glob = _globals

    def __call__(self, func, *args, **kwargs):  # only called when used as a decorator
        self.label = self.label or func.__name__
        self.func = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            runnable, src = make_runnable(func, _globals=get_caller_globals(self._glob))
            if self.verbose:
                print(src)

            if isnotasynccallable(func):
                with self:
                    for _ in range(self.best_of):
                        for iterations in autorange_generator():
                            with GCManager():
                                time_taken = runnable(iterations, self.timer, *args, **kwargs)
                                if time_taken >= self.min_duration:
                                    self.maxOpS = max(self.maxOpS, iterations / time_taken)
                                    break
                    return func(*args, **kwargs)
            elif isasynccallable(func):

                async def tmp():
                    with self:
                        for _ in range(self.best_of):
                            for iterations in autorange_generator():
                                with GCManager():
                                    time_taken = await runnable(iterations, self.timer, *args, **kwargs)
                                    if time_taken >= self.min_duration:
                                        self.maxOpS = max(self.maxOpS, iterations / time_taken)
                                        break
                    return await func(*args, **kwargs)

                return tmp()

        return wrapper

    def __enter__(self):
        self.maxOpS = 0.0
        self.label = self.label or label_from_frame(sys._getframe())
        if self.func is None:
            self.start_time = self.timer()
        return self

    def __exit__(self, *exc):
        if self.func is None:
            self.maxOpS = 1 / (self.timer() - self.start_time)

        print_bench(self.label or "default", self.maxOpS, *self.args, **self.kwargs)
        self.ops = 0.0


try:
    import gc

    default_disable_gc = True
except:
    default_disable_gc = False


class GCManager(ContextDecorator):
    def __init__(self, disable_gc=default_disable_gc):
        self.disable_gc = disable_gc

    def __enter__(self):
        if self.disable_gc:
            self.gcold = gc.isenabled()
            gc.disable()
        return self

    def __exit__(self, *exc):
        if self.disable_gc and self.gcold:
            gc.enable()


def autorange_generator():
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            yield iterations
        i *= 10


def get_caller_globals(_globals):
    g = sys._getframe(2).f_globals if _globals is None else _globals()
    return g | {"itertools": globals()["itertools"]}


def transform_ast_func(f):
    code = textwrap.dedent(inspect.getsource(f))
    module_tree = ast.parse(code).body[0]  # this creates a module
    if not isinstance(module_tree, ast.FunctionDef | ast.AsyncFunctionDef):
        raise ValueError(f"Expected a function, got {module_tree.__class__.__name__}")

    rewrite_returns(module_tree)
    lines = [ast.unparse(code_line).strip() for code_line in module_tree.body]

    func_name = f"bench_{module_tree.name}"
    func_args = ast.unparse(module_tree.args)
    func_body = "\n".join(lines).strip()

    return func_name, func_args, func_body


def rewrite_returns(body):
    class ReturnToContinueTransformer(ast.NodeTransformer):
        def visit_Return(self, node):
            return [ast.Assign(targets=[ast.Name(id="_", ctx=ast.Store())], value=node.value), ast.Continue()]

    ReturnToContinueTransformer().visit(body)
    ast.fix_missing_locations(body)


def reindent(src, indent):
    """Helper to reindent a multi-line statement."""
    return src.replace("\n", "\n" + " " * indent)


template = """
{async_stmt}def {func_name}(iters, _timer{init}):
    it = itertools.repeat(None, iters)
    
    __t0 = _timer()
    for _ in it:
        {stmt}
    __t1 = _timer()
    return __t1 - __t0
"""


def make_runnable(func: MaybeAsyncCallable[P, R], _globals):
    local_ns = {}
    init = ""
    func_name, func_args, func_body = transform_ast_func(func)
    if func_args != "":
        init += f", {func_args}"
    if asyncio.iscoroutinefunction(func):
        async_stmt = "async "
    else:
        async_stmt = ""
    stmt = reindent(func_body, 8)

    if stmt == "":
        stmt = "pass"

    src = template.format(func_name=func_name, func_args=func_args, stmt=stmt, async_stmt=async_stmt, init=init)
    code = compile(src, "<timeit-src>", "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)

    exec(code, _globals, local_ns)
    return local_ns[func_name], src


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


def _repr(arg):
    if isinstance(arg, Sized):
        l = len(arg)
        if l > 10:
            return f"{type(arg).__name__}[{l}]"
        return repr(arg)
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
