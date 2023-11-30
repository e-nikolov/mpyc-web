"""
This module provides a client for establishing connections with other peers using the PeerJS protocol.
"""

import asyncio

import logging
from typing import Any, Callable, Awaitable

# pyright: reportMissingImports=false
from pyodide.ffi import JsProxy, to_js
import rich
import rich.text
from mpyc import asyncoro  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=import-error,disable=no-name-in-module
from .transport import PeerJSTransport, AbstractClient
from lib.stats import stats
from . import api
from .run_mpc import run_mpc

from mpycweb.api.run import run_code
import js

logger = logging.getLogger(__name__)


def noop(*args, **kwargs):
    pass


loop = asyncio.get_event_loop()


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

    def __init__(self, async_proxy: api.AsyncRuntimeProxy, _loop: asyncio.AbstractEventLoop):
        self._loop = _loop

        self.transports = {}
        self.async_proxy = async_proxy

        async_proxy.on_ready_message = self.on_ready_message
        async_proxy.on_runtime_message = self.on_runtime_message
        async_proxy.on_run_mpc = run_mpc
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
        self.async_proxy.send("proxy:js:mpc:msg:ready", pid, message)

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
        # self._loop.create_task(self.transports[pid].on_ready_message(message))

    # @stats.acc(lambda self, pid, message: stats.total_calls() | stats.sent_to(pid, message))
    # @stats.time()
    @stats.acc(lambda self, pid, message: stats.sent_to(pid, message))
    def send_runtime_message(self, pid: int, message: bytes):
        # logger.debug(message)
        # logger.info("send_runtime_message")
        # logger.info(["runtime", pid, message])
        # logger.info(to_js(["runtime", pid, message]))
        self.async_proxy.send("proxy:js:mpc:msg:runtime", pid, message)
        # self._loop.create_task(self.async_proxy.send("proxy:js:mpc:msg:runtime", pid, message))
        # asyncio.ensure_future(self.async_proxy.send("proxy:js:mpc:msg:runtime", pid, message))
        # loop.create_task(self.async_proxy.send("proxy:js:mpc:msg:runtime", pid, message))

    # @stats.acc(lambda self, pid, message: stats.total_calls() | stats.received_from(pid, message))
    # @stats.set(lambda self, pid, message: stats.received_from(pid, message))
    @stats.acc(lambda self, pid, message: stats.received_from(pid, message))
    def _on_runtime_message(self, pid: int, message: bytes):
        # self._loop.create_task(self.transports[pid].on_runtime_message(message))
        self.transports[pid].on_runtime_message(message)

    def on_runtime_message(self, pid: int, message: JsProxy) -> None:
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
        # self._loop.create_task(self._on_runtime_message(pid, message.to_py()))
        # self._loop.call_soon(self._on_runtime_message, pid, message.to_py())
        self._on_runtime_message(pid, message.to_py())
