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
    def __init__(self, declaration: stmt.Function, closure: Environment):
        self._declaration = declaration
        # This environment is of when the function was declared not when it is called
        # which is what we want in this case, as it represents the lexical surroundings
        # of the function declaration.
        self._closure = closure

    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        # This would allow us to have variables scoped in the enclosing environment
        # of the function declaration and above.
        environment = Environment(enclosing=self._closure)
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

    def bind(self, instance):
        # type of instance is `ClassInstance`
        # we would get a circular import if we import it here
        environment = Environment(enclosing=self._closure)
        environment.define("this", instance)
        # `this` keyword is treated like a variable in enclosing environment that points
        # to `ClassInstance` instance
        return Function(self._declaration, environment)
