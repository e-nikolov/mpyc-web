# pyright: reportMissingImports=false
import asyncio

from mpycweb.debug import *

# from mpyc.runtime import mpc
from mpycweb import *

# TODO refactor to fire an event instead of printing
# logging.info("PyScript runtime started.")
asyncio.get_event_loop().call_soon(xworker.sync.onWorkerReady)

import polyscript
import pyodide
import pyscript
import sys
import logging

# logging.debug(f"PyScript {pyscript.version =}")
# logging.debug(f"Polyscript {polyscript.version =}")
logging.debug(f"Python {sys.version=}")
logging.debug(f"Pyodide {pyodide.__version__ =}")
