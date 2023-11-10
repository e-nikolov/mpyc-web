"""
    Shim for the PyScript port of MPyC.
"""

# pyright: reportMissingImports=false

import js
import logging


from mpycweb.lib.exception_handler import exception_handler
import asyncio


asyncio.get_event_loop().set_exception_handler(exception_handler)

try:
    RUNNING_IN_WORKER = not hasattr(js, "document")
    if RUNNING_IN_WORKER:
        from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

    import mpycweb

    # await run_file("test.py")  # pyright: ignore
except Exception as e:
    logging.error(
        e,
        exc_info=True,
        stack_info=True,
    )
