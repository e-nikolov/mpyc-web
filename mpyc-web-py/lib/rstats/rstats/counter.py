from typing import Any, TypeVar

from .types import NestedDict, Numeric

K = TypeVar("K")


class DeepCounter(NestedDict[K, Numeric | Any]):
    """A nested dictionary that stores numeric values and supports recursive updates.

    This class extends the `NestedDict` class and adds two methods for updating its values:
    `set` and `update`. Both methods take a nested dictionary as input and update the values
    in the `DeepCounter` instance recursively, i.e., for each key in the input dictionary,
    the corresponding value is either added to the current value (for `update`) or replaced
    by the input value (for `set`).

    The `DeepCounter` class is parameterized by two type variables: `K` and `Numeric`.
    `K` represents the type of the keys in the nested dictionary, while `Numeric` represents
    the type of the numeric values that can be stored in the dictionary.

    Example usage:
    ```
    >>> counter = DeepCounter[int, float]()
    >>> counter.set({1: {2: 3.0}})
    >>> counter.update({1: {2: 1.5}})
    >>> counter
    {1: {2: 4.5}}
    ```
    """

    def get(self, *path: K, default=None) -> Numeric | Any:
        d = self
        for key in path[:-1]:
            d = d.setdefault(key, {})
            if not isinstance(d, dict):
                raise TypeError(f"Invalid value of type {type(d)} for key {key}")

        if path[-1] in d:
            return d[path[-1]]

        d[path[-1]] = default
        return default

    def set(self, value: Numeric, *path: K):
        d = self
        for key in path[:-1]:
            d = d.setdefault(key, {})
            if not isinstance(d, dict):
                raise TypeError(f"Cannot set {type(value)} to {type(d)} for key {key}")

        d[path[-1]] = value

    def increment(self, value: Numeric, *path: K):
        # d = self.state
        d = self
        for key in path[:-1]:
            # Create a nested dictionary if key does not exist
            d = d.setdefault(key, {})
            if not isinstance(d, dict):
                raise TypeError(f"Cannot set {type(value)} to {type(d)} for key {key}")
        last_key = path[-1]

        old_val = d.setdefault(last_key, 0)

        if not isinstance(old_val, Numeric):
            raise TypeError(f"Cannot add {type(value)} and {type(old_val)} for key {last_key}")

        d[last_key] = old_val + value

    def apply(self, func, *path: K):
        d = self
        for key in path[:-1]:
            d = d.setdefault(key, {})
            if not isinstance(d, dict):
                raise TypeError(f"Cannot apply {func} to {type(d)} for key {key}")

        last_key = path[-1]
        d[last_key] = func(d[last_key])
