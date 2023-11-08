from pyodide.ffi import JsProxy, to_js
import js  # pyright: ignore[reportMissingImports] pylint: disable=import-error


def display(msg):
    """
    Displays a message.

    Args:
        msg (str): The message to display.
    """
    js.mpyc.display(msg)


def display_error(msg):
    """
    Displays a message.

    Args:
        msg (str): The message to display.
    """
    js.mpyc.displayError(msg)
