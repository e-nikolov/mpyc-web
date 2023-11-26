import logging
import types
import typing
import asyncio
import ast
import importlib.util
from lib.exception_handler import exception_handler


import pyodide
import micropip  # pyright: ignore[reportMissingImports] pylint: disable=import-error

from mpyc.runtime import Party, mpc  # pyright: ignore[reportMissingImports] pylint: disable=import-error,disable=no-name-in-module
from lib.stats import stats

from mpycweb.api.run import run_code

logger = logging.getLogger(__name__)

from lib.log import *
import os
import linecache

loop = asyncio.get_event_loop()


def run_mpc(options) -> None:
    """
    Runs an mpyc execution with the given options.

    Args:
        options (Namespace): The options for the mpyc execution.

    Returns:
        None
    """
    logger.debug("starting mpyc execution...")
    logger.debug(options)

    try:
        os.makedirs(os.path.dirname(options.filename), exist_ok=True)

        with open(options.filename, "w") as f:  # for rich tracebacks
            f.write(options.code)
            linecache.clearcache()
    except Exception as e:
        logger.warn(e)

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
    asyncio.get_event_loop().set_exception_handler(exception_handler)

    loop.create_task(run_code(options.code, options.filename))