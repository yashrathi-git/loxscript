from abc import ABC, abstractmethod
import typing as t

from .environment import Environment
from ..errors import Return

from ..parser import stmt


class Callable(ABC):
    @abstractmethod
    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        pass

    @property
    @abstractmethod
    def arity(self) -> int:
        return 102

    def __str__(self):
        return repr(self)


class Function(Callable):
    def __init__(self, declaration: stmt.Function):
        self._declaration = declaration

    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        environment = Environment(interpreter.globals)
        # The function is being called
        # we know the name of positional args from `arg_value` which comes from
        # function declaration
        for arg_name, arg_value in zip(self._declaration.params, arguments):
            environment.define(arg_name.lexeme, arg_value)
        try:
            interpreter.execute_block(self._declaration.body, environment=environment)
        except Return as e:
            return e.value

    def __repr__(self):
        return f"<fn {self._declaration.name.lexeme}>"

    @property
    def arity(self) -> int:
        return len(self._declaration.params)
