from os import environ
import os

# pyright: reportMissingImports=false
from polyscript import xworker
import asyncio
import rich
import pyodide


def print_tasks():
    print(asyncio.current_task())
    print(asyncio.all_tasks())


def ping():
    return True


def load_env():
    os.environ.update(get_env())


def get_env() -> dict[str, str]:
    return xworker.sync.getEnv().to_py()


import rich


def __update_environ(env):
    assert isinstance(env, dict)
    environ.update(env)
    cols = os.environ.get("COLUMNS")
    if cols and rich._console:
        rich._console.width = int(cols)


xworker.sync.ping = ping

import asyncio

loop = asyncio.get_event_loop()
xworker.sync.update_environ = lambda envProxy: loop.call_soon(__update_environ, envProxy.to_py())
