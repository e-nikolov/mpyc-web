import logging
import types
import typing
import asyncio
import ast
import importlib.util

import pyodide
import micropip  # pyright: ignore[reportMissingImports] pylint: disable=import-error

from mpyc.runtime import Party, mpc  # pyright: ignore[reportMissingImports] pylint: disable=import-error,disable=no-name-in-module
from mpycweb.lib.stats import stats

from mpycweb.api.run import run_code

logger = logging.getLogger(__name__)


async def run_mpc(options):
    """
    Runs an mpyc execution with the given options.

    Args:
        options (Namespace): The options for the mpyc execution.

    Returns:
        None
    """
    logger.debug("starting mpyc execution...")
    logger.debug(options)

    # m = len(options["parties"])
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

    return await run_code(options.code)
