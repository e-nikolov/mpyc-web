"""
This module defines logging functionality for the mpyc-web project.

It defines a custom logging handler that uses the rich library to format log messages with emojis and colors.
It also defines a function to set the log level and a custom function to print a directory tree.
"""

import io
import datetime
from pathlib import Path
from collections.abc import Iterable
import sys
from logging import LogRecord
import logging
import asyncio

from rich.console import Console
from rich.logging import RichHandler


from rich.text import Text
from rich.style import Style


from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error
from pyodide.ffi import JsProxy, to_js
from .stats import stats


CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
NOTSET = logging.NOTSET
INFO = logging.INFO
DEBUG = logging.DEBUG


console = Console(
    color_system="truecolor",
    force_terminal=True,
    tab_size=4,
    soft_wrap=True,
    safe_box=False,
    legacy_windows=False,
    force_interactive=True,
)


def set_log_level(level):
    """
    Set the log level for the application.

    Args:
        level (int): The log level to set. Must be one of the constants defined in the logging module.
    """
    opts: dict = dict(
        force=True,
        format="%(message)s",
        datefmt="[%X]",
        level=level,
        handlers=[
            Handler(
                markup=True,
                show_time=True,
                rich_tracebacks=True,
                tracebacks_word_wrap=False,
                tracebacks_show_locals=True,
                omit_repeated_times=False,
            )
        ],
    )

    logging.basicConfig(**opts)

    sys.argv = ["", "--log-level", logging.getLevelName(level)]
    stats.reset()


class Handler(RichHandler):
    """
    Custom logging handler that extends RichHandler to provide additional functionality.

    Overrides the get_level_emoji and render methods to customize the log output.
    """

    def _get_level_message(self, record: LogRecord, message_renderable):
        text = message_renderable

        match record.levelname:
            case "CRITICAL":
                level = Text.styled(" 🔥".ljust(3))
            case "ERROR":
                text.style = Style(color="red")
                # level = Text.styled(" ❌".ljust(3))
                level = Text.styled(" ✖".ljust(3), style=Style(color="red"))
            case "WARNING":
                level = Text.styled(" ⚠️".ljust(3))
            case "INFO":
                # level = Text.styled(" ℹ".ljust(3))
                level = Text.styled(" 🛈".ljust(3), style=Style(color="yellow"))
            case "DEBUG":
                # level = Text.styled("🐞 🪲 ⬤ ℹ️ ⚙️ 🔧 🛠 ⚒ 🛠️ ".ljust(3))
                level = Text.styled(" ⚒".ljust(3), style=Style(color="grey50"))
                text.style = Style(color="grey50")
            case _:
                level = Text.styled(record.levelname.ljust(3))

        return (level, text)

    def render(self, *, record, traceback, message_renderable):
        path = Path(record.pathname).name
        (level, message) = self._get_level_message(record, message_renderable)
        time_format = None if self.formatter is None else self.formatter.datefmt
        log_time = datetime.datetime.fromtimestamp(record.created)
        path = f"{path}:{record.lineno}"
        if record.funcName not in ["<module>", "<lambda>"]:
            path = f"{path}:{record.funcName}"
        log_renderable = self._log_render(
            self.console,
            [message] if not traceback else [message, traceback],
            log_time=log_time,
            time_format=time_format,
            level=level,
            path=path,
            link_path=f"{record.pathname}#{record.lineno}" if self.enable_link_path else None,
        )
        return log_renderable


loop = asyncio.get_event_loop()


def display(msg):
    """
    Displays a message.

    Args:
        msg (str): The message to display.
    """
    xworker.postMessage(to_js(["display", msg]))
    # xworker.sync.display(msg)


def display_error(msg):
    """
    Displays a message.

    Args:
        msg (str): The message to display.
    """
    xworker.postMessage(to_js(["display:error", msg]))
    # xworker.sync.displayError(msg)


class TermWriter(io.StringIO):
    """
    A custom class that extends io.StringIO and overrides the write and writelines methods to display text in the notebook.
    """

    def __init__(self, print_fn) -> None:
        self.print_fn = print_fn

    def write(self, text):
        self.print_fn(text)

    def writelines(self, __lines: Iterable[str]) -> None:
        for line in __lines:
            self.print_fn(f"{line}\n")


def print_tree(path_str=".", prefix="", text=""):
    """
    Print a directory tree.

    Args:
        path (Path): The path to the directory to print.
        prefix (str): The prefix to use for each line of the tree.
        str (str): The string to append to each line of the tree.
    """
    path = Path(path_str)

    for item in path.iterdir():
        print(f"{prefix}├── {item.name}\n")
        if item.is_dir():
            print_tree(item, prefix + "│   ", text)
