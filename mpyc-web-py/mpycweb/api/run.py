import logging
import types
import typing
import asyncio
import ast
import importlib.util

import js
import pyodide
import micropip  # pyright: ignore[reportMissingImports] pylint: disable=import-error

from mpyc.runtime import Party, mpc  # pyright: ignore[reportMissingImports] pylint: disable=import-error,disable=no-name-in-module
from mpycweb.lib.stats import stats

logger = logging.getLogger(__name__)


async def run_file(file: str):
    """
    Executes the given Python file asynchronously, loading any missing packages first.

    Args:
        file (string): The Python file to execute.

    Returns:
        None
    """

    try:
        with open(file, "r", encoding="utf-8") as f:
            code = f.read()
            return await run_code(code)
    except Exception as e:
        logging.error(
            e,
            exc_info=True,
            stack_info=True,
        )
        raise e


async def run_code_async(source: str, filename: str):
    """
    Compiles and runs the given Python source code asynchronously.

    Args:
        source (str): The Python source code to compile and run.

    Returns:
        The result of running the compiled code.
    """
    code = compile(source, filename, "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    func: typing.Callable = types.FunctionType(code, globals() | {"__name__": "__main__"})
    if asyncio.iscoroutinefunction(func):
        return await func()  # pylint: disable=not-callable

    return func()  # pylint: disable=not-callable


import rich

import traceback


async def run_code(code: str, filename=None):
    """
    Executes the given Python code asynchronously, loading any missing packages first.

    Args:
        code (str): The Python code to execute.

    Returns:
        None
    """
    await load_missing_packages(code)
    # return await run_code_async(code, filename)
    await pyodide.code.eval_code_async(code, globals() | {"__name__": "__main__"}, filename=filename)
    # try:
    #     await load_missing_packages(code)
    #     # return await run_code_async(code, filename)
    #     await pyodide.code.eval_code_async(code, globals() | {"__name__": "__main__"}, filename=filename)
    # except Exception as e:
    #     rich.inspect(
    #         e,
    #         all=True,
    #     )
    #     traceback.print_exception(e)
    #     rich.inspect(
    #         e.__traceback__,
    #         all=True,
    #     )
    #     pass
    #     # logging.error(
    #     #     e,
    #     #     exc_info=True,
    #     #     stack_info=True,
    #     # )
    #     # raise e


async def load_missing_packages(code: str):
    """
    Installs packages required by the given code.

    Args:
        code (str): The code to check for required packages.

    Returns:
        None
    """

    try:
        await js.pyodide.loadPackagesFromImports(
            code
            #  {"message_callback": js.wrap.io.stdout, "message_callback_stderr": js.wrap.io.stderr}
        )
        imports = pyodide.code.find_imports(code)
        imports = [item for item in imports if importlib.util.find_spec(item) is None]
        if len(imports) > 0:
            # logging.info(f"Loading packages: {imports}")
            await micropip.install(imports, keep_going=True)
    except Exception as e:
        logging.error(
            e,
            exc_info=True,
            stack_info=True,
        )
        raise e
