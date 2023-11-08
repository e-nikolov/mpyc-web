import typing

from pyodide.ffi import JsProxy, to_js

from .in_worker import IN_WORKER

if IN_WORKER:
    from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

    def send_message(_type: str, pid: int, message: typing.Any):
        xworker.postMessage(to_js([_type, pid, message]))

else:
    import js  # pyright: ignore[reportMissingImports] pylint: disable=import-error

    def send_message(_type: str, pid: int, message: typing.Any):
        js.mpyc.sendMessage(to_js([_type, pid, message]))
