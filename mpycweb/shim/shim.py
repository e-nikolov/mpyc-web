"""
    Shim for the PyScript port of MPyC.
"""

from pyodide.code import run_js

# https://github.com/pyodide/pyodide/issues/4006
# The pyodide Webloop relies onsetTimeout(), which has a minimum delay of 4ms
# this slows down code that uses await asyncio.sleep(0)
# This monkey patch replaces setTimeout() with a faster version that uses MessageChannel
run_js("""
async function getCallSoon_pool() {
    pool = await import('https://cdn.jsdelivr.net/npm/generic-pool@3.9.0/+esm')
        
    const channelPool = pool.createPool(
        {
            create: async () => {
                return new MessageChannel();
            },
            destroy: async (channel) => {
                channel.port1.close();
                channel.port2.close();
            }
        },
        {
            min: 1000,
            max: 20000,
            //         // maxWaitingClients: 1000,
            //         // testOnBorrow: true,
            //         // testOnReturn: true,
            //         // acquireTimeoutMillis: 1000,
            //         // fifo: true,
            //         // priorityRange: 10,
            //         // autostart: true,
            //         // evictionRunIntervalMillis: 1000,
            //         // numTestsPerEvictionRun: 100,
            //         // softIdleTimeoutMillis: 1000,
            //         // idleTimeoutMillis: 1000,
        })

    self.callSoon = function (callback, delay) {
        if (delay == undefined || isNaN(delay) || delay < 0) {
            delay = 0;
        }
        if (delay < 1) {
            channelPool.acquire().then(channel => {
                channel.port1.onmessage = () => { channelPool.release(channel); callback() };
                channel.port2.postMessage('');
            });
        } else {
            setTimeout(callback, delay);
        }
    }

    self.channelPool = channelPool
    return self.callSoon
}
        """)

import js

from pyodide import webloop

webloop.setTimeout = await js.getCallSoon_pool()
# pyright: reportMissingImports=false
import sys
import io
from collections.abc import Iterable
import time
import logging
import asyncio

import pyodide
from pyodide.ffi import JsProxy, to_js
import pyodide_js

RUNNING_IN_WORKER = not hasattr(js, "document")

if RUNNING_IN_WORKER:
    from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error


def exceptHook(*args):
    js.console.error("except hook")
    logging.error("exceptHook")
    logging.error(
        *args,
        exc_info=True,
        stack_info=True,
    )


def onerr(*args, **kwargs):
    js.console.error("onerror")
    logging.error("onerror")
    logging.error(
        *args,
        exc_info=True,
        stack_info=True,
    )


def onmessageerr(*args, **kwargs):
    js.console.error("onmessageerr")
    logging.error("onmessageerr")
    logging.error(
        *args,
        exc_info=True,
        stack_info=True,
    )
    # logging.error(*args, **kwargs)


sys.excepthook = exceptHook

xworker.onerror = onerr
xworker.onmessageerror = onmessageerr

from mpycweb import *

# from mpycweb.bootstrap import *
# from mpycweb import *
# await run_file("test.py")  # pyright: ignore
# except Exception as e:
#     logging.error(
#         e,
#         exc_info=True,
#         stack_info=True,
#     )
