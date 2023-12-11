import asyncio
import logging
import os
from enum import StrEnum, auto
from typing import Any, Awaitable, Callable, Coroutine, Dict, List, Literal, Tuple, TypeVarTuple

import js
import rich
from lib.stats import stats
from pyodide.ffi import JsProxy, to_js
from pyodide.http import pyfetch

from .run import run_code

logger = logging.getLogger(__name__)

RUNNING_IN_WORKER = not hasattr(js, "document")


class ProxyEventType(StrEnum):
    # MPC_READY = 1
    # MPC_RUNTIME = 2
    # MPC_EXEC = 3
    # PY_EXEC = 4
    # PY_ENV_UPDATE = 5

    MPC_READY = "proxy:py:mpc:ready"
    MPC_RUNTIME = "proxy:py:mpc:runtime"
    MPC_EXEC = "proxy:py:mpc:exec"
    EXEC = "proxy:py:exec"
    ENV_UPDATE = "proxy:py:env:update"
    STATS_RESET = "proxy:py:stats:reset"
    STATS_TOGGLE = "proxy:py:stats:toggle"
    STATS_SHOW = "proxy:py:stats:show"
    STATS_HIDE = "proxy:py:stats:hide"


class ProxyEvent:
    # data: list[ProxyEventType, *Ts]
    data: Tuple[ProxyEventType, Any]


# type ProxyEvent = Literal("proxy:py:mpc:ready") | "proxy:py:mpc:runtime" | "proxy:py:mpc:exec" | "proxy:py:exec" | "proxy:py:env:update" | "proxy:py:ping"


class SyncRuntimeProxy:
    def __init__(self, chan: Any):
        self.chan = chan

    def fetch(self, filename: str):
        return self.chan.fetch(filename)

    def readline(self, prompt: str):
        return self.chan.readline(prompt)

    def get_env(self):
        return self.chan.getEnv().to_py()

    def load_env(self):
        """
        Loads environment variables from a .env file and updates the current environment.

        Returns:
            None
        """
        os.environ.update(self.get_env())


import rich

loop = asyncio.get_event_loop()
import time
from datetime import datetime


class AsyncRuntimeProxy:
    postMessage: Callable[[Any], Awaitable[None]]
    on_ready_message: Callable[[int, str], None]
    on_runtime_message: Callable[[int, JsProxy], None]
    on_run_mpc: Callable[[Any], None]
    chan: Any

    def __init__(self, chan: Any):
        self.chan = chan
        chan.onmessage = self.onmessage
        self.postMessage = chan.postMessage

    async def fetch(self, filename: str, **opts):
        return pyfetch(filename, **opts)
 
    # async def send(self, _type: str, pid: int, message: Any):
    def send(self, _type: str, pid: int, message: Any):
        self.postMessage(to_js([_type, pid, [message, time.time_ns() // 1000]]))

    # async def notify_runtime_ready(self):
    def notify_runtime_ready(self):
        js.console.log("runtime ready")
        self.postMessage(to_js(["proxy:js:runtime:ready"]))
 
    def onmessage(self, event: ProxyEvent):
        try:
            self._onmessage(event)
        except Exception as e:
            logger.error(e, exc_info=True, stack_info=True)

    def _onmessage(self, event: ProxyEvent):

        # js.console.error("onmessage")
        # [message_type, *rest] = event.data.to_py()
        [message_type, *rest] = event.data

        match message_type: 
            case ProxyEventType.STATS_TOGGLE:
                stats.enabled = not stats.enabled
            case ProxyEventType.STATS_SHOW:
                stats.enabled = True
            case ProxyEventType.STATS_HIDE:
                stats.enabled = False
            case ProxyEventType.STATS_RESET:
                stats.reset()
            case ProxyEventType.MPC_READY:
                [pid, message] = rest
                message, ts = message.to_py()

                self.on_ready_message(pid, message)
                # loop.create_task(self.on_ready_message(pid, message))
                # loop.call_soon(on_ready_message, pid, message)
            case ProxyEventType.MPC_RUNTIME:
                pid, message = rest

                message, ts = message.to_py()

                self.on_runtime_message(pid, message, ts)
                # loop.create_task(self.on_runtime_message(pid, message))
                # loop.call_soon(on_runtime_message, pid, message)
            case ProxyEventType.MPC_EXEC:
                [opts] = rest
                self.on_run_mpc(opts)
                # loop.create_task(self.on_run_mpc(opts))
                # loop.call_soon(run_mpc, opts)
            case ProxyEventType.EXEC:
                [code] = rest
                # run_code(code)
                loop.create_task(run_code(code))
                # loop.call_soon(run_mpc, opts)
            case ProxyEventType.ENV_UPDATE:
                [env] = rest
                on_update_env(env.to_py())
                # api.loop.call_soon(api.update_env, env.to_py())
            case _:
                logger.warning(f"Received unknown message type {message_type}")

    async def display(self, msg):
        """
        Displays a message.

        Args:
            msg (str): The message to display.
        """
        self.chan.postMessage(to_js(["proxy:js:display", msg]))

    async def display_error(self, msg):
        """
        Displays a message.

        Args:
            msg (str): The message to display.
        """
        self.chan.postMessage(to_js(["proxy:js:display:error", msg]))


async_proxy = None
sync_proxy = None


if RUNNING_IN_WORKER:
    from polyscript import xworker

    async_proxy = AsyncRuntimeProxy(xworker)
    sync_proxy = SyncRuntimeProxy(xworker.sync)

else:
    sync_proxy = SyncRuntimeProxy(js.MPCRuntimeSyncChannel)
    async_proxy = AsyncRuntimeProxy(js.MPCRuntimeAsyncChannel)


async def stats_printer():
    while True:
        async_proxy.postMessage(to_js(["proxy:js:display:stats", str(stats.to_tree())]))
        await asyncio.sleep(2)


def on_update_env(env):
    assert isinstance(env, dict)
    if rich._console:  # pylint: disable=protected-access
        os.environ.update(env)
        cols = os.environ.get("COLUMNS")
        lines = os.environ.get("LINES")
        # js.console.log("environ/COLUMNS", os.environ["COLUMNS"])
        # js.console.log("environ/LINES", os.environ["LINES"])

        if cols:
            rich._console.width = int(cols)  # pylint: disable=protected-access
        if lines:
            rich._console.height = int(lines)  # pylint: disable=protected-access
