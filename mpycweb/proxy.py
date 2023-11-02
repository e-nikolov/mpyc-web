"""
This module provides a client for establishing connections with other peers using the PeerJS protocol.
"""

import asyncio

import logging
from typing import Any, Callable

# pyright: reportMissingImports=false
from pyodide.ffi import JsProxy, to_js
import rich
import rich.text
from mpyc import asyncoro  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=import-error,disable=no-name-in-module
from .transport import PeerJSTransport, AbstractClient
from .lib.stats import stats
from . import api
from .run_mpc import run_mpc
import js

logger = logging.getLogger(__name__)


def noop():
    pass


loop = asyncio.get_event_loop()


def onmessage(on_ready_message=noop, on_runtime_message=noop):
    def _on_message(event):
        # js.console.error("onmessage")

        # [message_type, *rest] = event.data.to_py()
        [message_type, *rest] = event.data

        match message_type:
            case "proxy:py:mpc:ready":
                [pid, message] = rest
                on_ready_message(pid, message)
                # loop.call_soon(on_ready_message, pid, message)
            case "proxy:py:mpc:runtime":
                [pid, message] = rest
                on_runtime_message(pid, message)
                # loop.call_soon(on_runtime_message, pid, message)
            case "proxy:py:mpc:exec":
                [opts] = rest
                asyncio.ensure_future(run_mpc(opts))
                # loop.call_soon(run_mpc, opts)
            case "proxy:py:env:update":
                [env] = rest
                api.update_env(env.to_py())
                # api.loop.call_soon(api.update_env, env.to_py())
            case "proxy:py:ping":
                api.ping()
                # api.loop.call_soon(api.ping)
            case _:
                logger.warning(f"Received unknown message type {message_type}")

    return _on_message


api.chanAsync.onmessage = onmessage()
# xworker.onmessage = onmessage()


class Client(AbstractClient):
    """
    A client for establishing connections with other peers using the PeerJS protocol.

    Args:
        worker (Any): The worker object for sending and receiving messages.
        loop (AbstractEventLoop): The event loop for scheduling tasks.

    Attributes:
        worker (Any): The worker object for sending and receiving messages.
        loop (AbstractEventLoop): The event loop for scheduling tasks.
        transports (Dict[int, PeerJSTransport]): A dictionary of active transports, indexed by peer ID.

    Methods:
        create_connection(protocol_factory, loop, pid, listener): Creates a new connection with a peer.
        send_ready_message(pid, message): Sends a ready message to a peer.
        on_ready_message(pid, message): Receives a ready message from a peer.
        send_runtime_message(pid, message): Sends a runtime message to a peer.
        on_runtime_message(pid, message): Receives a runtime message from a peer.
    """

    def __init__(self, _loop: asyncio.AbstractEventLoop):
        self.loop = _loop

        self.transports = {}
        api.chanAsync.onmessage = onmessage(self.on_ready_message, self.on_runtime_message)
        # xworker.onmessage = onmessage(self.on_ready_message, self.on_runtime_message)

    async def create_connection(
        self, protocol_factory: Callable[[], asyncoro.MessageExchanger], loop: asyncio.AbstractEventLoop, pid: int, listener: bool
    ) -> tuple[asyncio.Transport, asyncio.Protocol]:
        """
        Creates a new connection with the given protocol factory and event loop.

        Args:
            protocol_factory (Callable[[], asyncoro.MessageExchanger]): A callable that returns a new instance of a protocol.
            loop (AbstractEventLoop): The event loop to use for the connection.
            pid (int): The ID of the peer to connect to.
            listener (bool): Whether or not this peer is a listener.

        Returns:
            tuple[Transport, Protocol]: A tuple containing the transport and protocol objects for the new connection.
        """
        p = protocol_factory()
        t = PeerJSTransport(loop, pid, self, p, listener)
        self.transports[pid] = t
        return t, p

    # @stats.acc(lambda self, pid, message: stats.total_calls() | stats.sent_to(pid, message))
    @stats.acc(lambda self, pid, message: stats.sent_to(pid, message))
    def send_ready_message(self, pid: int, message: str):
        api.send_message("proxy:js:mpc:msg:ready", pid, message)

    # @stats.acc(lambda self, pid, message: stats.total_calls() | stats.received_from(pid, message))
    @stats.acc(lambda self, pid, message: stats.received_from(pid, message))
    def on_ready_message(self, pid: int, message: str):
        """
        Handle a 'ready' message from a peer.

        Args:
            pid (int): The ID of the peer sending the message.
            message (str): The message content.

        Returns:
            None
        """
        if pid not in self.transports:
            logger.warning(f"Received ready message from {pid} but no transport exists for that pid yet")
            return
        self.transports[pid].on_ready_message(message)

    # @stats.acc(lambda self, pid, message: stats.total_calls() | stats.sent_to(pid, message))
    # @stats.time()
    @stats.acc(lambda self, pid, message: stats.sent_to(pid, message))
    def send_runtime_message(self, pid: int, message: bytes):
        # logger.debug(message)
        # logger.info("send_runtime_message")
        # logger.info(["runtime", pid, message])
        # logger.info(to_js(["runtime", pid, message]))
        api.send_message("proxy:js:mpc:msg:runtime", pid, message)

    # @stats.acc(lambda self, pid, message: stats.total_calls() | stats.received_from(pid, message))
    # @stats.set(lambda self, pid, message: stats.received_from(pid, message))
    @stats.acc(lambda self, pid, message: stats.received_from(pid, message))
    def _on_runtime_message(self, pid: int, message: bytes):
        self.transports[pid].on_runtime_message(message)

    def on_runtime_message(self, pid: int, message: JsProxy):
        """
        Handle a runtime message from a peer.

        Args:
            pid (int): The ID of the peer sending the message.
            message (JsProxy): The message received from the peer.
        """
        # logger.info("on_runtime_message")
        # logger.info(type(message))
        # logger.info(message)
        # logger.info(message.to_memoryview())
        # logger.info(message.to_bytes())
        # logger.info(type(message))
        self._on_runtime_message(pid, message.to_bytes())
