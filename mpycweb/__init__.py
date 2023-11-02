"""
This module provides the main functionality of the mpyc-web package, which allows for secure multi-party computation
in a web environment.
"""

# pylint: disable=wrong-import-position,wrong-import-order

import time
import asyncio
import logging
import rich
import rich.pretty


noop = lambda *args, **kwargs: None

# display = noop
# display_error = noop

try:
    from mpycweb.api import *

    from mpycweb.lib.term_writer import *

    import sys

    # sys.stdout = TermWriter(display)
    # sys.stderr = TermWriter(display_error)

    from mpycweb.lib.log import *

    from mpycweb.lib import log

    rich._console = log.console  # pylint: disable=protected-access
    import builtins

    builtins.print = rich.print

    import pprint

    pprint.pprint = rich.pretty.pprint
    log.setup()

    from mpycweb.lib.log_levels import *

    lvl = DEBUG
    # sys.argv = ["main.py", "--log-level", f"{logging.getLevelName(lvl)}"]
    api.load_env()
    set_log_level(lvl)

    logger = log.getLogger(__name__)

    # def exceptHook(*args):
    #     logging.exception(
    #         *args,
    #         exc_info=True,
    #         stack_info=True,
    #     )

    # sys.excepthook = exceptHook

    import pyodide

    logger.debug(f"Python version={sys.version}")
    logger.debug(f"Pyodide version={pyodide.__version__}")

    import mpyc

    logger.debug(
        f"MPyC version={mpyc.__version__}"
    )  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=no-member,c-extension-no-member

    from .transport import *

    from .patches import *
    from .lib.bench import *

    from .run_mpc import *

    __all__ = [
        "log",
        "stats",
        "patches",
        "transport",
        "run",
        "run_code",
        "run_file",
        "set_log_level",
        "print_tree",
        "bench",
        "NOTSET",
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
        "RUNNING_IN_WORKER",
    ]

    api.onWorkerReady()

    asyncio.create_task(api.stats_printer())

except Exception as e:
    logging.error(
        e,
        exc_info=True,
        stack_info=True,
    )
