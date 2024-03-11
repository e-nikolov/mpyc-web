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
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, Sized, TypeGuard, TypeVar, overload

if len(logging.root.handlers) == 0:
    logging.basicConfig(level=logging.INFO)

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
default_timer = time.time


def bench(_globals=None, best_of=default_best_of, verbose=False, min_duration=default_min_duration, timer: Callable[[], float] = default_timer):
    @overload
    def _bench(func: AsyncCallable[P, R]) -> AsyncCallable[P, R]: ...

    @overload
    def _bench(func: Callable[P, R]) -> Callable[P, R]: ...

    def _bench(func: MaybeAsyncCallable[P, R]) -> MaybeAsyncCallable[P, R]:
        if isasynccallable(func):
            return _bench_async(func, _glob=_globals, best_of=best_of, verbose=verbose, min_duration=min_duration, timer=timer)
        elif isnotasynccallable(func):
            return _bench_sync(func, _glob=_globals, best_of=best_of, verbose=verbose, min_duration=min_duration, timer=timer)

        raise TypeError("Invalid function type")

    return _bench


def to_runnable(src, func_name, _globals=None):
    local_ns = {}
    code = compile(src, "<timeit-src>", "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)

    exec(code, _globals, local_ns)
    return local_ns[func_name]


def _bench_sync(
    func: Callable[P, R], _glob=None, best_of=default_best_of, verbose=False, min_duration=default_min_duration, timer: Callable[[], float] = default_timer
) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        # _globals = sys._getframe().f_back.f_globals
        print_bench_start(func.__name__, *args, **kwargs)

        maxOpS = 0.0
        src, func_name = make_timeit_source(func)
        if verbose:
            print(src)

        runnable = to_runnable(src, func_name, _globals=get_caller_globals(_glob))
        for _ in range(best_of):
            for iterations in autorange_generator():
                with GCManager():
                    time_taken = runnable(iterations, timer, *args, **kwargs)
                if time_taken >= default_min_duration:
                    maxOpS = max(maxOpS, iterations / time_taken)
                    break
        res = func(*args, **kwargs)
        print_bench_end(func.__name__, maxOpS, *args, **kwargs)
        return res

    return wrapper


def _bench_async(
    func: AsyncCallable[P, R], _glob=None, best_of=default_best_of, verbose=False, min_duration=default_min_duration, timer: Callable[[], float] = default_timer
) -> AsyncCallable[P, R]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs):
        print_bench_start(func.__name__, *args, **kwargs)
        maxOpS = 0.0
        src, func_name = make_timeit_source(func)
        if verbose:
            print(src)
        runnable = to_runnable(src, func_name, _globals=get_caller_globals(_glob))
        for _ in range(best_of):
            for iterations in autorange_generator():
                with GCManager():
                    time_taken = await runnable(iterations, timer, *args, **kwargs)
                if time_taken >= min_duration:
                    maxOpS = max(maxOpS, iterations / time_taken)
                    break

        res = await func(*args, **kwargs)
        print_bench_end(func.__name__, maxOpS, *args, **kwargs)
        return res

    return wrapper


try:
    import gc

    default_disable_gc = True
except:
    default_disable_gc = False


class GCManager(ContextDecorator):
    def __init__(self, disable_gc=default_disable_gc):
        # def __init__(self, func, _globals, iters, disable_gc=default_disable_gc):
        self.disable_gc = disable_gc
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


def autorange_generator():
    i = 1
    while True:
        for j in 1, 2, 5:
            iterations = i * j
            yield iterations
        i *= 10


import rich


def get_caller_globals(_globals):
    g = sys._getframe(2).f_globals if _globals is None else _globals()
    return g | {"itertools": globals()["itertools"]}


def transform_ast_func(f, doc_string=False):
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
        def visit_FunctionDef(self, node: ast.FunctionDef):
            if node is body:
                self.generic_visit(node)
            else:
                return node

        def visit_Return(self, node):
            return [ast.Assign(targets=[ast.Name(id="_", ctx=ast.Store())], value=node.value), ast.Raise(exc=ast.Name(id="FakeReturnException"), cause=None)]

    ReturnToContinueTransformer().visit(body)
    ast.fix_missing_locations(body)


def reindent(src, indent):
    """Helper to reindent a multi-line statement."""
    return src.replace("\n", "\n" + " " * indent)


template = """
{async_stmt}def {func_name}(___iters, _timer{init}):
    ___it = itertools.repeat(None, ___iters)
    class FakeReturnException(Exception): ...

    __t0 = _timer()
    for _ in ___it:
        try:
            {stmt}
        except FakeReturnException:
            pass
    __t1 = _timer()
    return __t1 - __t0
"""


def make_timeit_source(func: MaybeAsyncCallable[P, R]):
    init = ""
    func_name, func_args, func_body = transform_ast_func(func)
    if func_args != "":
        init += f", {func_args}"
    if asyncio.iscoroutinefunction(func):
        async_stmt = "async "
    else:
        async_stmt = ""
    stmt = reindent(func_body, 12)

    if stmt == "":
        stmt = "pass"
    return template.format(func_name=func_name, func_args=func_args, stmt=stmt, async_stmt=async_stmt, init=init), func_name


def format_ops(ops: float) -> str:
    return f"{round(ops):,} ops/sec"


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


def print_bench_start(label: str, *args, **kwargs):
    logging.info(f"{label}{format_args(*args, **kwargs)}: Starting...")


def print_bench_end(label: str, ops: float, *args, **kwargs):
    logging.info(f"{label}{format_args(*args, **kwargs)}: {format_ops(ops)}")
