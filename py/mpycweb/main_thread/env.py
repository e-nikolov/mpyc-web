import logging
import asyncio
import os

import pyodide
import js  # pyright: ignore[reportMissingImports] pylint: disable=import-error


def get_env() -> dict[str, str]:
    """
    Returns a dictionary containing the environment variables of the worker process.

    Returns:
        A dictionary containing the environment variables of the worker process.
    """
    return js.mpyc.getEnv().to_py()

    # return xworker.sync.getEnv().to_py()


def load_env():
    """
    Loads environment variables from a .env file and updates the current environment.

    Returns:
        None
    """
    os.environ.update(get_env())
