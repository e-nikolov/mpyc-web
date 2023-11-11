import typing

from pyodide.ffi import JsProxy, to_js

from .channels import RUNNING_IN_WORKER, chanAsync


def send_message(_type: str, pid: int, message: typing.Any):
    chanAsync.postMessage(to_js([_type, pid, message]))
