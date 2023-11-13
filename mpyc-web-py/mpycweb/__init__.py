"""
This module provides the main functionality of the mpyc-web package, which allows for secure multi-party computation
in a web environment.
"""

from rich.traceback import install

install(show_locals=True)
import js

js.console.log("mpyc-web-py")
# pylint: disable=wrong-import-position,wrong-import-order

__all__ = [
    "log",
    "set_log_level",
    "ls",
    "NOTSET",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

import asyncio


from pyodide import webloop
import js

webloop.setTimeout = js.fastSetTimeout

from . import api
from lib.exception_handler import exception_handler


import asyncio
import logging
import rich
import rich.pretty
import sys

import pyodide

from lib.log_levels import *
from lib.log import *
from lib import log

api.sync_proxy.load_env()
log.install(DEBUG)

logger = logging.getLogger(__name__)


import mpyc

logger.debug(f"MPyC version={mpyc.__version__}")  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=no-member,c-extension-no-member

from .transport import *
from .patches import *
from lib.bench import *

api.async_proxy.notify_runtime_ready()

asyncio.create_task(api.stats_printer())


logger.debug(f"Python version={sys.version}")
(a, b, c) = sys._emscripten_info.emscripten_version  # pyright: ignore
logger.debug(f"Emscripten version={a}.{b}.{c}")
logger.debug(f"Pyodide version={pyodide.__version__}")
