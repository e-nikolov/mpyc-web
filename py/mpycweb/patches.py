from asyncio import Future
import time
import types

from .debug import *

from .transport import *
from .worker import *
from mpyc.runtime import mpc, Runtime
import datetime
import logging

logger = logging.getLogger(__name__)

# pyright: reportMissingImports=false
from polyscript import xworker
from pyodide.code import run_js
import pyodide.webloop as webloop

import js

from pyodide.ffi import create_once_callable
from rich import print

from . import peerjs
from .stats import stats

# https://github.com/pyodide/pyodide/issues/4006
# The pyodide Webloop relies onsetTimeout(), which has a minimum delay of 4ms
# this slows down code that uses await asyncio.sleep(0)
# This monkey patch replaces setTimeout() with a faster version that uses MessageChannel
run_js("""
//import genericPool from 'https://cdn.jsdelivr.net/npm/generic-pool@3.9.0/+esm'

console.log(globalThis.pyodide)

const oldSetTimeout = setTimeout;

function fastSetTimeout(callback, delay) {
    if (delay == undefined || isNaN(delay) || delay < 0) {
        delay = 0;
    }
    if (delay < 1) {
        const channel = new MessageChannel();
        channel.port1.onmessage = () => { callback() };
        channel.port2.postMessage('');
    } else {
        oldSetTimeout(callback, delay);
    }
}


// import pool from 'generic-pool'

// const channelPool = pool.createPool(
//     {
//         create: async () => {
//             return new MessageChannel();
//         },
//         destroy: async (channel) => {
//             channel.port1.close();
//             channel.port2.close();
//         }
//     },
//     {
//         max: 100,
//         min: 30,
//     }
// )

// export function callSoon(callback: () => void, delay: number = 0) {
//     if (delay == undefined || isNaN(delay) || delay < 0) {
//         delay = 0;
//     }
//     if (delay < 1) {
//         channelPool.acquire().then(channel => {
//             channel.port1.onmessage = () => { channelPool.release(channel); callback() };
//             channel.port2.postMessage('');
//         });
//     } else {
//         setTimeout(callback, delay);
//     }
// }



console.warn("test pyodide worker")
        """)
webloop.setTimeout = js.fastSetTimeout


# async def stats_printer():
#     while True:
#         xworker.sync.log(f"Python Worker Stats")
#         xworker.sync.log(f"{stats.stats}")
#         await asyncio.sleep(5)


# asyncio.ensure_future(stats_printer())


def run(self, f):
    """Run the given coroutine or future until it is done."""
    logger.debug(f"monkey patched run() {f.__class__.__name__}")

    if self._loop.is_running():
        if not asyncio.iscoroutine(f):
            f = asyncoro._wrap_in_coro(f)
            while True:
                try:
                    f.send(None)
                except StopIteration as exc:
                    return exc.value
        else:
            return asyncio.ensure_future(f)
    # TODO await in JS? https://github.com/pyodide/pyodide/issues/1219
    return self._loop.run_until_complete(f)


mpc.run = types.MethodType(run, mpc)


# The regular start() starts TCP connections, which don't work in the browser.
# We monkey patch it to use PeerJS instead.
async def start(runtime: Runtime) -> None:
    loop = runtime._loop

    pjs = peerjs.Client(xworker.sync, loop)

    # TODO refactor runtime.start() to work with multiple transports
    """Start the MPyC runtime with a PeerJS transport.

    Open connections with other parties, if any.
    """
    logger.debug("monkey patched start()")
    logger.info(f"Start MPyC runtime v{runtime.version} with a PeerJS transport")
    logger.info(f"{len(mpc.parties)} parties, threshold={mpc.options.threshold}, no_async={mpc.options.no_async}")
    runtime.start_time = time.time()

    m = len(runtime.parties)
    if m == 1:
        return

    # m > 1
    for peer in runtime.parties:
        peer.protocol = asyncio.Future(loop=loop) if peer.pid == runtime.pid else None

    # Listen for all parties < runtime.pid.

    # Connect to all parties > self.pid.
    for peer in runtime.parties:
        if peer.pid == runtime.pid:
            continue

        logger.debug(f"Connecting to {peer}")

        while True:
            try:
                if peer.pid > runtime.pid:
                    factory = lambda: asyncoro.MessageExchanger(runtime, peer.pid)
                    listener = False
                else:
                    factory = lambda: asyncoro.MessageExchanger(runtime)
                    listener = True

                logger.debug(f"Creating peerjs connection to {peer.pid} (listener: {listener})...")

                await pjs.create_connection(factory, runtime._loop, peer.pid, listener)

                logger.debug(f"Creating peerjs connection to {peer.pid} (listener: {listener})... done")
                break
            except asyncio.CancelledError:
                raise

            except Exception as exc:
                logger.debug(exc)
            await asyncio.sleep(1)

    logger.info("Waiting for all parties to connect")
    await runtime.parties[runtime.pid].protocol
    logger.info(f"All {m} parties connected.")


mpc.start = types.MethodType(start, mpc)


async def shutdown(self):
    """Shutdown the MPyC runtime.

    Close all connections, if any.
    """
    # Wait for all parties behind a barrier.
    logger.debug("monkey patched shutdown()")

    while self._pc_level > self._program_counter[1]:
        await asyncio.sleep(0)
    elapsed = time.time() - self.start_time
    logger.info(f"Stop MPyC runtime -- elapsed time: {datetime.timedelta(seconds=elapsed)}")
    m = len(self.parties)
    if m == 1:
        return

    # m > 1
    self.parties[self.pid].protocol = Future(loop=self._loop)
    logger.info("Synchronize with all parties before shutdown")
    await self.gather(self.transfer(self.pid))

    # Close connections to all parties > self.pid.
    logger.info("Closing connections with other parties")
    # TODO refactor to make this work with closing only the connections to peers with pid > self.pid
    for peer in self.parties:
        if peer.pid == self.pid:
            continue
        logger.debug("Closing connection with peer %d", peer.pid)
        peer.protocol.close_connection()
    await self.parties[self.pid].protocol

    stats.print_stats()


mpc.shutdown = types.MethodType(shutdown, mpc)
