import logging
import asyncio
from os import environ
import os
import rich

import pyodide
from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

from mpycweb import api


def get_env() -> dict[str, str]:
    """
    Returns a dictionary containing the environment variables of the worker process.

    Returns:
        A dictionary containing the environment variables of the worker process.
    """
    return xworker.sync.getEnv().to_py()


def load_env():
    """
    Loads environment variables from a .env file and updates the current environment.

    Returns:
        None
    """
    os.environ.update(get_env())
