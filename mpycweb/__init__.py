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

    if IN_WORKER:
        from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

        xworker.sync.run_mpc = lambda *args, **kwargs: asyncio.ensure_future(run_mpc(*args, **kwargs))

        xworker.sync.update_environ = lambda envProxy: api.loop.call_soon(api.update_environ, envProxy.to_py())

        xworker.sync.ping = api.ping

    sys.stdout = TermWriter(display)
    sys.stderr = TermWriter(display_error)

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
    set_log_level(lvl)

    logger = log.getLogger(__name__)

    def exceptHook(*args):
        logging.exception(
            *args,
            exc_info=True,
            stack_info=True,
        )

    sys.excepthook = exceptHook

    from pyodide.code import run_js

    import pyodide

    logger.debug(f"Python version={sys.version}")
    logger.debug(f"Pyodide version={pyodide.__version__}")

    import mpyc

    logger.debug(
        f"MPyC version={mpyc.__version__}"
    )  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=no-member,c-extension-no-member

    from .transport import *

    # from .worker import *
    from .patches import *
    from .lib.bench import *

    from mpycweb.mpc.run_mpc import *

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
        "IN_WORKER",
    ]

    api.onWorkerReady()

    asyncio.create_task(api.stats_printer())

    # from mpycweb.bootstrap import *
    # from mpycweb import *
except Exception as e:
    logging.error(
        e,
        exc_info=True,
        stack_info=True,
    )

loop = asyncio.get_event_loop()

# from .worker.worker_init import *
# from .worker import worker_init
