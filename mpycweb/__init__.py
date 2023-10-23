"""
This module provides the main functionality of the mpyc-web package, which allows for secure multi-party computation
in a web environment.
"""

# pylint: disable=wrong-import-position,wrong-import-order

import time
import asyncio


from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error


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

sys.stdout = TermWriter()
sys.stderr = TermWriter()


rich._console = log.console  # pylint: disable=protected-access
import builtins

builtins.print = rich.print
import pprint

import rich.pretty

pprint.pprint = rich.pretty.pprint

set_log_level(DEBUG)

import pyodide

# import micropip
from pyodide.code import run_js

# import pyodide_js


# await micropip.install("emfs:./mpyc-0.9-py3-none-any.whl")

# rich.inspect(pyodide_js)


# import pyscript


# logging.debug(f"PyScript {pyscript.version =}")
# logging.debug(f"Polyscript {polyscript.version =}")

logging.debug(f"Python version={sys.version}")
logging.debug(f"Pyodide version={pyodide.__version__}")

import mpyc

logging.debug(
    f"MPyC version={mpyc.__version__}"  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=no-member,c-extension-no-member
)

from .transport import *
from .worker import *
from .patches import *

__all__ = [
    "log",
    "stats",
    "patches",
    "transport",
    "worker",
    "set_log_level",
    "print_tree",
    "NOTSET",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

xworker.sync.log("pyscript ready")

asyncio.get_event_loop().call_soon(xworker.sync.onWorkerReady)
