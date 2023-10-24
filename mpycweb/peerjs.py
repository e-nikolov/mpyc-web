"""
This module provides a client for establishing connections with other peers using the PeerJS protocol.
"""

from asyncio import AbstractEventLoop, Protocol, Transport
import logging
from typing import Any, Callable

# pyright: reportMissingImports=false
from pyodide.ffi import JsProxy, to_js
from mpyc import asyncoro  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=import-error,disable=no-name-in-module
from .transport import PeerJSTransport, AbstractClient
from .stats import stats
from polyscript import xworker

logger = logging.getLogger(__name__)
import rich


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

    def __init__(self, loop: AbstractEventLoop):
        self.loop = loop

        self.transports = {}
        xworker.onmessage = self._on_message

    def _on_message(self, event):
        # rich.inspect(event)
        # rich.inspect(message.data)
        [message_type, pid, message] = event.data

        if message_type == "ready":
            self.on_ready_message(pid, message)
        elif message_type == "runtime":
            self.on_runtime_message(pid, message)
        else:
            logger.warning(f"Received unknown message type {message_type}")

    async def create_connection(
        self, protocol_factory: Callable[[], asyncoro.MessageExchanger], loop: AbstractEventLoop, pid: int, listener: bool
    ) -> tuple[Transport, Protocol]:
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

    @stats.acc(lambda self, pid, message: stats.total_calls() | stats.sent_to(pid, message))
    def send_ready_message(self, pid: int, message: str):
        xworker.postMessage(to_js(["ready", pid, message]))

    @stats.acc(lambda self, pid, message: stats.total_calls() | stats.received_from(pid, message))
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

    @stats.acc(lambda self, pid, message: stats.total_calls() | stats.sent_to(pid, message))
    def send_runtime_message(self, pid: int, message: bytes):
        # logger.debug(message)
        # xworker.postMessage(to_js(["runtime", pid, message]), to_js(message))
        xworker.postMessage(to_js(["runtime", pid, message]))

    @stats.acc(lambda self, pid, message: stats.total_calls() | stats.received_from(pid, message))
    def _on_runtime_message(self, pid: int, message: bytes):
        self.transports[pid].on_runtime_message(message)

    def on_runtime_message(self, pid: int, message: JsProxy):
        """
        Handle a runtime message from a peer.

        Args:
            pid (int): The ID of the peer sending the message.
            message (JsProxy): The message received from the peer.
        """
        # logger.info(message.to_py())
        # logger.info(message.to_memoryview())
        # logger.info(message.to_bytes())
        # logger.info(type(message))
        self._on_runtime_message(pid, message.to_bytes())


# x = to_js([1, 2, 3])
# y = to_js(["test1", "test2"])
# xworker.postMessage(x, y)


# def on_message(args):
#     print("before on message")
#     print(args)
#     print("after on message")
