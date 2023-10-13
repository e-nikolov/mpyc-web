from asyncio import AbstractEventLoop, Future, Protocol, Transport
import logging
from typing import Any, Callable

logging = logging.getLogger(__name__)

# pyright: reportMissingImports=false
from mpyc import asyncoro
from mpyc.runtime import mpc, Party, Runtime
from .debug import *
from . import worker
from .transport import PeerJSTransport, AbstractClient
from pyodide.ffi import JsProxy
from .stats import stats


class Client(AbstractClient):
    def __init__(self, worker: Any, loop: AbstractEventLoop):
        self.worker = worker
        self.loop = loop

        self.worker.on_ready_message = self.on_ready_message
        self.worker.on_runtime_message = self.on_runtime_message

        self.transports = {}
        self.i = 0

    async def create_connection(
        self, protocol_factory: Callable[[], asyncoro.MessageExchanger], loop: AbstractEventLoop, pid: int, listener: bool
    ) -> tuple[Transport, Protocol]:
        p = protocol_factory()
        t = PeerJSTransport(loop, pid, self, p, listener)
        self.transports[pid] = t
        return t, p

    @stats.acc(lambda self, pid, message: stats.total_calls() | stats.sent_to(pid, message))
    def send_ready_message(self, pid: int, message: str):
        # self.loop.call_soon(self.worker.sendReadyMessage, pid, message)
        self.worker.sendReadyMessage(pid, message)

    @stats.acc(lambda self, pid, message: stats.total_calls() | stats.received_from(pid, message))
    def on_ready_message(self, pid: int, message: str):
        if pid not in self.transports:
            logger.warning(f"Received ready message from {pid} but no transport exists for that pid yet")
            return
        # self.loop.call_soon(self.transports[pid].on_ready_message, message)
        self.transports[pid].on_ready_message(message)

    @stats.acc(lambda self, pid, message: stats.total_calls() | stats.sent_to(pid, message))
    def send_runtime_message(self, pid: int, message: bytes):
        # self.i += 1
        # i = self.i
        # self.worker.logWarn(f"send_runtime_message 1 {i}")
        # self.loop.call_soon(self.worker.sendRuntimeMessage, pid, message)
        self.worker.sendRuntimeMessage(pid, message)

        # self.worker.logWarn(f"send_runtime_message 99 {i}")

    @stats.acc(lambda self, pid, message: stats.total_calls() | stats.received_from(pid, message.to_py()))
    def on_runtime_message(self, pid: int, message: JsProxy):
        # self.loop.call_soon(self.transports[pid].on_runtime_message, message.to_py())
        self.transports[pid].on_runtime_message(message.to_py())
