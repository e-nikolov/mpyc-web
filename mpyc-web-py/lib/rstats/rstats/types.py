import asyncio
from typing import Any, Awaitable, Callable, ParamSpec, TypedDict, TypeGuard, TypeVar

Numeric = int | float

_K = TypeVar("_K")
_V = TypeVar("_V")

NestedDict = dict[_K, _V | "NestedDict[_K, _V]"]

PS = ParamSpec("PS")
R = TypeVar("R")
T = TypeVar("T")

type AsyncCallable[**P, R] = Callable[P, Awaitable[R]]
type MaybeAsyncCallable[**P, R] = AsyncCallable[P, R] | Callable[P, R]
type TimerFunc = Callable[[], float]


def isasynccallable[**P, R](func: MaybeAsyncCallable[P, R]) -> TypeGuard[AsyncCallable[P, R]]:
    return asyncio.iscoroutinefunction(func)


def isnotasynccallable[**P, R](func: MaybeAsyncCallable[P, R]) -> TypeGuard[Callable[P, R]]:
    return not asyncio.iscoroutinefunction(func)
