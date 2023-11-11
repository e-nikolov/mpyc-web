"""
This module provides the main functionality of the mpyc-web package, which allows for secure multi-party computation
in a web environment.
"""

from rich.traceback import install

install(show_locals=True)
raise Exception("aaaaaaaaa")
# pylint: disable=wrong-import-position,wrong-import-order

__all__ = [
    "log",
    "stats",
    "set_log_level",
    "print_tree",
    "NOTSET",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


from pyodide import webloop
import js

webloop.setTimeout = js.fastSetTimeout

import asyncio
import logging
import rich
import rich.pretty
import sys


from mpycweb.lib.log_levels import *
from mpycweb.lib.log import *
from mpycweb.lib import log

rich._console = log.console  # pylint: disable=protected-access
import builtins


builtins.print = rich.print

import pprint

pprint.pprint = rich.pretty.pprint
# log.setup()

from mpycweb import api

api.load_env()
lvl = DEBUG
# sys.argv = ["main.py", "--log-level", f"{logging.getLevelName(lvl)}"]
# set_log_level(lvl)
logger = logging.getLogger(__name__)


import pyodide


import mpyc

logging.debug(
    f"MPyC version={mpyc.__version__}"
)  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=no-member,c-extension-no-member

from .transport import *
from .patches import *
from .lib.bench import *
from .run_mpc import *


api.onWorkerReady()

asyncio.create_task(api.stats_printer())


js.console.log("python version")
logger.debug(f"Python version={sys.version}")
(a, b, c) = sys._emscripten_info.emscripten_version
logging.debug(f"Emscripten version={a}.{b}.{c}")
logging.debug(f"Pyodide version={pyodide.__version__}")
raise Exception("???????")
