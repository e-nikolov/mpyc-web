"""
This module contains functions for initializing the worker process.

Functions:
- print_tasks: Prints the current asyncio task and all running tasks.
- ping: Returns True to indicate that the worker process is running and responsive.
- load_env: Loads environment variables from a .env file and updates the current environment.
- get_env: Returns a dictionary containing the environment variables of the worker process.
"""

from os import environ
import os
import asyncio

# pyright: reportMissingImports=false

from polyscript import xworker  # pylint: disable=import-error
import rich


async def print_tasks():
    """
    Prints the current asyncio task and all running tasks.

    Returns:
        None
    """
    print(asyncio.current_task())
    print(asyncio.all_tasks())


def ping():
    """
    Returns True to indicate that the worker process is running and responsive.
    """
    return True


def load_env():
    """
    Loads environment variables from a .env file and updates the current environment.

    Returns:
        None
    """
    os.environ.update(get_env())


def get_env() -> dict[str, str]:
    """
    Returns a dictionary containing the environment variables of the worker process.

    Returns:
        A dictionary containing the environment variables of the worker process.
    """
    return xworker.sync.getEnv().to_py()


def __update_environ(env):
    assert isinstance(env, dict)
    if rich._console:  # pylint: disable=protected-access
        environ.update(env)
        cols = os.environ.get("COLUMNS")
        lines = os.environ.get("LINES")

        if cols:
            rich._console.width = int(cols)  # pylint: disable=protected-access
        if lines:
            rich._console.height = int(lines)  # pylint: disable=protected-access


xworker.sync.ping = ping

loop = asyncio.get_event_loop()
xworker.sync.update_environ = lambda envProxy: loop.call_soon(__update_environ, envProxy.to_py())
