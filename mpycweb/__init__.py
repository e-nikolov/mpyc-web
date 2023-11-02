"""
This module provides the main functionality of the mpyc-web package, which allows for secure multi-party computation
in a web environment.
"""

# pylint: disable=wrong-import-position,wrong-import-order

import time
import asyncio
from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

from .bootstrap import *


loop = asyncio.get_event_loop()


def sleep_logger(secs: float) -> None:
    """
    Sleeps for a given number of seconds and logs a warning message.

    Args:
        secs (float): The number of seconds to sleep for.
    """
    loop.call_soon(xworker.sync.logWarn, f"sleeping for {secs} seconds")
    # xworker.sync.logWarn(f"sleeping for {secs} seconds")

    old_time_sleep(secs)


old_time_sleep = time.sleep
time.sleep = sleep_logger

from .worker_init import *
from . import worker_init


worker_init.load_env()

from .log import *
from . import log

import sys

sys.stdout = TermWriter(display)
sys.stderr = TermWriter(display_error)


rich._console = log.console  # pylint: disable=protected-access
import builtins

builtins.print = rich.print

import pprint

import rich.pretty

pprint.pprint = rich.pretty.pprint
log.setup()

lvl = DEBUG
sys.argv = ["main.py", "--log-level", f"{logging.getLevelName(lvl)}"]
set_log_level(lvl)

import logging

logger = log.getLogger(__name__)


def exceptHook(*args):
    logging.exception(
        *args,
        exc_info=True,
        stack_info=True,
    )


sys.excepthook = exceptHook

from pyodide.code import run_js

import pyodide

logger.debug(f"Python version={sys.version}")
logger.debug(f"Pyodide version={pyodide.__version__}")

import mpyc

logger.debug(f"MPyC version={mpyc.__version__}")  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=no-member,c-extension-no-member

from .transport import *
from .worker import *
from .patches import *
from .bench import *

__all__ = [
    "log",
    "stats",
    "patches",
    "transport",
    "worker",
    "bootstrap",
    "run_code",
    "run_file",
    "set_log_level",
    "print_tree",
    "bench",
    "NOTSET",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

xworker.sync.log("pyscript ready")

asyncio.get_event_loop().call_soon(xworker.sync.onWorkerReady)

from rich.live import Live


async def stats_printer():
    while True:
        xworker.postMessage(to_js(["stats", str(stats.to_tree())]))
        await asyncio.sleep(1)
    # with Live(auto_refresh=False, get_renderable=stats.to_tree) as live:
    #     while True:
    #         live.refresh()
    #         await asyncio.sleep(1000)


asyncio.ensure_future(stats_printer())
