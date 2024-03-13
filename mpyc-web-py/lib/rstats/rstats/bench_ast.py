# pylint: disable-all

import ast
import asyncio
import inspect
import logging
import textwrap
import time
from contextlib import ContextDecorator
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeGuard, TypeVar

from .types import MaybeAsyncCallable, isasynccallable, isnotasynccallable


def reindent(src, indent):
    """Helper to reindent a multi-line statement."""
    return src.replace("\n", "\n" + " " * indent)


template = """
import itertools

@goto
{async_stmt}def {func_name}(___iters, ___timer{args_src}):
    ___it = itertools.repeat(None, ___iters)
    class FakeReturnException(Exception): ...
    ___t0 = ___timer()
    label .___start
    
    for _ in ___it:
        {body_src}
    ___t1 = ___timer()
    return ___t1 - ___t0
"""


def make_timeit_source[**P, R](func_name: str, func: MaybeAsyncCallable[P, R]):
    func_ast = parse_func_ast(func)
    has_returns = transform_func_ast(func_ast)
    async_stmt = "async " if isasynccallable(func) else ""
    return template.format(func_name=func_name, args_src=unparse_func_args(func_ast.args), body_src=unparse_func_body(func_ast.body), async_stmt=async_stmt)


def parse_func_ast(func):
    code = textwrap.dedent(inspect.getsource(func))
    func_ast = ast.parse(code).body[0]
    if not isinstance(func_ast, ast.FunctionDef | ast.AsyncFunctionDef):
        raise ValueError(f"Expected a function, got {func_ast.__class__.__name__}")
    return func_ast


def unparse_func_args(args_ast: ast.arguments):
    args_src = ast.unparse(args_ast)
    return f", {args_src}" if args_src != "" else ""


def unparse_func_body(func_body: list[ast.stmt], has_returns=False):
    src_lines = [ast.unparse(code_line).strip() for code_line in func_body]
    body_src = "\n".join(src_lines).strip()
    body_src = body_src or "pass"

    if has_returns:
        body_src = reindent(body_src, 12)
        body_src = f"""
try:
    {body_src}
except FakeReturnException:
    pass
"""
    else:
        body_src = reindent(body_src, 8)

    return body_src


def transform_func_ast(func_ast):
    class FuncReturnTransformer(ast.NodeTransformer):
        def __init__(
            self,
        ):
            self.inside_inner_loop = False
            self.has_returns = False

            super().__init__()

        def visit_FunctionDef(self, node: ast.FunctionDef):
            if node is func_ast:  # only transform the top-level function's returns
                self.generic_visit(node)
            else:
                return node  # otherwise return it as is

        def visit_While(self, node: ast.While):
            old_inside_inner_loop = self.inside_inner_loop
            self.inside_inner_loop = True
            res = self.generic_visit(node)
            self.inside_inner_loop = old_inside_inner_loop
            return res

        def visit_For(self, node: ast.For):
            old_inside_inner_loop = self.inside_inner_loop
            self.inside_inner_loop = True
            res = self.generic_visit(node)
            self.inside_inner_loop = old_inside_inner_loop
            return res

        def visit_Return(self, node):
            self.has_returns = True
            stmts = []
            if node.value is not None:  # if the return has a value, we assign it to "_" to make sure it's evaluated
                stmts.append(ast.Assign(targets=[ast.Name(id="_", ctx=ast.Store())], value=node.value))

            # stmts.append(ast.BinOp(left="goto", op="", right="start"))
            stmts.append(ast.Expr(value=ast.Attribute(value=ast.Name(id="goto", ctx=ast.Load()), attr="___start", ctx=ast.Load())))
            # if not self.inside_inner_loop:  # we are inside our own loop, so we transform the return into a "continue", which is cheaper than a "raise"
            #     stmts.append(ast.Continue())
            # else:  # if we transform the "return" to "continue", we'll only continue the inner loop, so we raise instead
            #     stmts.append(ast.Raise(exc=ast.Name(id="FakeReturnException"), cause=None))

            return stmts

    t = FuncReturnTransformer()
    t.visit(func_ast)
    ast.fix_missing_locations(func_ast)
    return t.has_returns
