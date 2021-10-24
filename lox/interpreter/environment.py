import typing as t

from ..errors import RuntimeException
from ..lexer.token import Token


class Environment:
    def __init__(self, enclosing: t.Optional["Environment"] = None):
        self._variables: t.Dict[str, t.Any] = {}
        self._enclosing = enclosing

    def define(self, name: str, value: t.Any):
        # Here we are currently not checking to see if the variable to be declared
        # already exists, so same variable could be overridden using `var varname` again
        self._variables[name] = value

    def get(self, name: Token):
        try:
            return self._variables[name.lexeme]
        except KeyError:
            if self._enclosing is not None:
                # We first try to find the reference in the innermost environment
                # and if it is not found there we walk up the chain recursively.
                return self._enclosing.get(name)

            raise RuntimeException(name, f"Undefined variable {name.lexeme}")

    def assign(self, name: Token, value: t.Any):
        if name.lexeme in self._variables.keys():
            self._variables[name.lexeme] = value
            return
        if self._enclosing is not None:
            return self._enclosing.assign(name, value)
        raise RuntimeException(name, f"Undefined variable {name.lexeme}")

    def ancestor(self, distance: int) -> "Environment":
        environment = self
        for _ in range(distance):
            environment = environment._enclosing
        return environment

    def get_at(self, dist: int, name: str) -> t.Any:
        # We don't handle the case of KeyError because we know it will be there because
        # the resolver have found it before.
        return self.ancestor(dist)._variables[name]

    def assign_at(self, distance: int, name: str, value: t.Any) -> None:
        self.ancestor(distance)._variables[name] = value
