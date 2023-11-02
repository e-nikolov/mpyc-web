"""
worker.py
"""

import asyncio
import importlib
import logging

from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error
import pyodide.code
import micropip  # pyright: ignore[reportMissingImports] pylint: disable=import-error

from mpyc.runtime import Party, mpc  # pyright: ignore[reportMissingImports] pylint: disable=import-error,disable=no-name-in-module

from mpycweb import api
from mpycweb.run_mpc import run_mpc

# from mpycweb.log import *
from mpycweb.lib.stats import stats

# from .bootstrap import *
