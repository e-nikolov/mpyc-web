import typing

from pyodide.ffi import JsProxy, to_js

from .channels import RUNNING_IN_WORKER, chanAsync
