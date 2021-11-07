import sys
import time
import typing as t

from .callable import Callable


class Clock(Callable):
    @property
    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        return time.time()

    def __repr__(self):
        return "<native function>"


class GetChar(Callable):
    def __init__(self):
        self._input_text = None

    @property
    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        if self._input_text is None:
            inp = sys.stdin
            self._input_text = ""
            for line in inp:
                self._input_text += line
        if len(self._input_text) == 0:
            return float(-1)
        current_char = self._input_text[0]
        self._input_text = self._input_text[1:]
        return float(ord(current_char))

    def __repr__(self):
        return "<native function>"


class Chr(Callable):
    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        return chr(int(arguments[0]))

    @property
    def arity(self) -> int:
        return 1


class Exit(Callable):
    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        exit(arguments[0])

    @property
    def arity(self) -> int:
        return 1


class PrintError(Callable):
    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        print(arguments[0], file=sys.stderr)

    @property
    def arity(self) -> int:
        return 1
