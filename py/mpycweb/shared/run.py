"""
worker.py
"""

import asyncio
import importlib
import logging

import pyodide.code
import micropip  # pyright: ignore[reportMissingImports] pylint: disable=import-error
from .log import *
from ..bootstrap import *

from mpyc.runtime import Party, mpc  # pyright: ignore[reportMissingImports] pylint: disable=import-error,disable=no-name-in-module
from ..lib.stats import stats

logger = logging.getLogger(__name__)
