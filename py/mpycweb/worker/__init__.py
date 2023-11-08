"""
This module provides the main functionality of the mpyc-web package, which allows for secure multi-party computation
in a web environment.
"""

# pylint: disable=wrong-import-position,wrong-import-order

import time
import asyncio
from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

from mpycweb.shared import *

from .env import *
from ..api.disp import *
from .run import *

# from .transport import *
# from .worker.patches import *
# from .shared.bench import *

__all__ = [
    # "patches",
    # "transport",
    "run",
]

onWorkerReady = lambda: asyncio.get_event_loop().call_soon(xworker.sync.onWorkerReady)
