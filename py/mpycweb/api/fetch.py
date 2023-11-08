from os import environ
from .in_worker import IN_WORKER

# pyright: reportMissingImports=false


def fetch(filename: str):
    if IN_WORKER:
        from polyscript import xworker  # pyright: ignore[reportMissingImports] pylint: disable=import-error

        return xworker.sync.fetch(filename).to_py()
    else:
        import js  # pyright: ignore-all pylint: disable-all

        return js.mpyc.fetch(filename).to_py()
