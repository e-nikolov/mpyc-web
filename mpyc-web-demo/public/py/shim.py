"""
    Shim for the PyScript port of MPyC.
"""
# pyright: reportMissingImports=false

import logging
import asyncio
import pyodide

# import polyscript.xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error


try:
    from mpycweb import *

    # from mpycweb.bootstrap import *
    # from mpycweb import *
    if IN_WORKER:
        from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

    await run_file("test.py")  # pyright: ignore
except Exception as e:
    logging.error(
        e,
        exc_info=True,
        stack_info=True,
    )
