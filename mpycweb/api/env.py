from os import environ
import os
import asyncio

# pyright: reportMissingImports=false

import rich

from .channels import chanSync

loop = asyncio.get_event_loop()
import js
import logging


def ping():
    """
    Returns True to indicate that the worker process is running and responsive.
    """
    return True


def update_env(env):
    assert isinstance(env, dict)
    if rich._console:  # pylint: disable=protected-access
        environ.update(env)
        cols = os.environ.get("COLUMNS")
        lines = os.environ.get("LINES")
        js.console.log("environ/COLUMNS", os.environ["COLUMNS"])
        js.console.log("environ/LINES", os.environ["LINES"])

        if cols:
            rich._console.width = int(cols)  # pylint: disable=protected-access
        if lines:
            rich._console.height = int(lines)  # pylint: disable=protected-access


def load_env():
    """
    Loads environment variables from a .env file and updates the current environment.

    Returns:
        None
    """
    e = chanSync.getEnv()
    os.environ.update(e.to_py())
