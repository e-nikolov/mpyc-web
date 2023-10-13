import logging

from pathlib import Path
import sys
from typing import Optional, TypeVar, Any, Callable, ParamSpec
from functools import wraps


# pyright: reportMissingImports=false
from polyscript import xworker


logger = logging.getLogger(__name__)


# print_tree(Path("../"))
