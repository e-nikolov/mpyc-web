"""
    Shim for the PyScript port of MPyC.
"""
# pyright: reportMissingImports=false

import logging
import asyncio
import pyodide
from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error


try:
    from mpycweb.bootstrap import *
    from mpycweb import *

    await run_file("test.py")  # pyright: ignore
except Exception as e:
    logging.error(
        e,
        exc_info=True,
        stack_info=True,
    )
