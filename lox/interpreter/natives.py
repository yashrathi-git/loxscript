from .callable import Callable
import typing as t
import time


class Clock(Callable):
    @property
    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        return time.time()

    def __repr__(self):
        return "<native function>"
