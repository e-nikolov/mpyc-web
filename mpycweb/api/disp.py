from pyodide.ffi import JsProxy, to_js

from .in_worker import IN_WORKER

if IN_WORKER:
    from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

    def display(msg):
        """
        Displays a message.

        Args:
            msg (str): The message to display.
        """
        xworker.postMessage(to_js(["display", msg]))

    def display_error(msg):
        """
        Displays a message.

        Args:
            msg (str): The message to display.
        """
        xworker.postMessage(to_js(["display:error", msg]))

else:
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
