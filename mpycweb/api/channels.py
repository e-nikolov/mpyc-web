import logging
import asyncio

import pyodide
from pyodide.ffi import JsProxy, to_js
import js  # pyright: ignore[reportMissingImports] pylint: disable=import-error

from mpycweb.lib.stats import stats

RUNNING_IN_WORKER = not hasattr(js, "document")


class AsyncChan:
    def __init__(self, chan):
        self.chan = chan

    async def postMessage(self, *args, **kwargs):
        self.chan.postMessage(*args, **kwargs)


chanAsync = None
chanSync = None

if RUNNING_IN_WORKER:
    from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

    # chanAsync = AsyncChan(js)
    chanAsync = xworker
    chanSync = xworker.sync
else:
    # chanAsync = AsyncChan(js.MPCRuntimeAsyncChannel)
    chanAsync = js.MPCRuntimeAsyncChannel
    chanSync = js.MPCRuntimeSyncChannel


def onWorkerReady():
    js.console.log("runtime ready")
    chanAsync.postMessage(to_js(["proxy:js:runtime:ready"]))


async def stats_printer():
    while True:
        chanAsync.postMessage(to_js(["proxy:js:display:stats", str(stats.to_tree())]))
        await asyncio.sleep(1)


def readline(prompt: str):
    return chanSync.readline(prompt)
