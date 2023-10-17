"""
worker.py
"""


import asyncio
import logging
import types
import ast
import importlib

from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error
import pyodide.code
import micropip  # pyright: ignore[reportMissingImports] pylint: disable=import-error

from mpyc.runtime import Party, mpc  # pyright: ignore[reportMissingImports] pylint: disable=import-error,disable=no-name-in-module
from .stats import stats

logger = logging.getLogger(__name__)


async def run_mpc(options):
    """
    Runs an mpyc execution with the given options.

    Args:
        options (Namespace): The options for the mpyc execution.

    Returns:
        None
    """
    await load_missing_packages(options.code)

    logger.debug("starting mpyc execution...")

    m = len(options.parties)
    mpc.options.threshold = (m - 1) // 2
    mpc.options.no_async = m == 1 and options.no_async
    stats.reset()
    assert 2 * mpc.options.threshold < m, f"threshold {mpc.options.threshold} too large for {m} parties"

    parties = []
    for pid, peerID in enumerate(options.parties):
        parties.append(Party(pid, peerID))
    mpc.options.parties = parties

    # reinitialize the mpyc runtime with the new parties
    mpc.__init__(options.pid, parties, mpc.options)  # pylint: disable=unnecessary-dunder-call

    try:
        await pyodide.code.eval_code_async(options.code, globals() | {"__name__": "__main__"})
    except Exception as e:
        logger.error(e)

    # await run_code_async(options.code)


async def load_missing_packages(code: str):
    """
    Installs packages required by the given code.

    Args:
        code (str): The code to check for required packages.

    Returns:
        None
    """
    imports = pyodide.code.find_imports(code)
    imports = [item for item in imports if importlib.util.find_spec(item) is None]

    if len(imports) > 0:
        try:
            logging.info(f"Loading packages: {imports}")
            await micropip.install(imports, keep_going=True)
        except Exception as e:
            print(e)


def run_code(source: str):
    """
    Compiles and executes the given Python source code.

    Args:
        source (str): The Python source code to execute.

    Returns:
        The result of executing the code.
    """
    code = compile(source, "_mpc_run_compiled.py", "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    func = types.FunctionType(code, globals() | {"__name__": "__main__"})
    return func()  # pylint: disable=not-callable


async def run_code_async(source: str):
    """
    Compiles and runs the given Python source code asynchronously.

    Args:
        source (str): The Python source code to compile and run.

    Returns:
        The result of running the compiled code.
    """
    code = compile(source, "_mpc_run_compiled.py", "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    func = types.FunctionType(code, globals() | {"__name__": "__main__"})
    if asyncio.iscoroutinefunction(func):
        return await func()  # pylint: disable=not-callable

    return func()  # pylint: disable=not-callable


# asyncio.shield()
xworker.sync.run_mpc = lambda *args, **kwargs: asyncio.ensure_future(run_mpc(*args, **kwargs))


xworker.sync.print_stats = stats.print_stats
