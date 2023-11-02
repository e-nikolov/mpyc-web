import io
from collections.abc import Iterable


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
