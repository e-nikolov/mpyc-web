from pyodide.ffi import JsProxy, to_js

from .channels import RUNNING_IN_WORKER, chanAsync


def display(msg):
    """
    Displays a message.

    Args:
        msg (str): The message to display.
    """
    chanAsync.postMessage(to_js(["proxy:js:display", msg]))


def display_error(msg):
    """
    Displays a message.

    Args:
        msg (str): The message to display.
    """
    chanAsync.postMessage(to_js(["proxy:js:display:error", msg]))
