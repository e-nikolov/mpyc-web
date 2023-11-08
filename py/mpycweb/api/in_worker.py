import logging
import asyncio
import pyodide
from pyodide.ffi import JsProxy, to_js
from mpycweb.lib.stats import stats

try:
    from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

    IN_WORKER = True

    def onWorkerReady():
        xworker.sync.log("pyscript ready")
        asyncio.get_event_loop().call_soon(xworker.sync.onWorkerReady)

    async def stats_printer():
        while True:
            xworker.postMessage(to_js(["stats", str(stats.to_tree())]))
            await asyncio.sleep(1)

except ImportError:
    import js  # pyright: ignore-all pylint: disable-all

    def onWorkerReady():
        js.console.log("pyscript ready")
        asyncio.get_event_loop().call_soon(js.mpyc.onWorkerReady)

    async def stats_printer():
        while True:
            js.mpyc.updateStats(str(stats.to_tree()))
            await asyncio.sleep(1)

    IN_WORKER = False
