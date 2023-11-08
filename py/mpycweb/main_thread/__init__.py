"""
This module provides the main functionality of the mpyc-web package, which allows for secure multi-party computation
in a web environment.
"""

# pylint: disable=wrong-import-position,wrong-import-order

import time
import asyncio

from .disp import *

__all__ = [
    "display",
    "display_error",
]
