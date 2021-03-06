import typing as t

from loxscript.errors import RuntimeException
from loxscript.interpreter.callable import Callable, Function
from loxscript.lexer.token import Token


class ClassInstance:
    def __init__(self, klass: "Class"):
        self._klass = klass
        self._map = {}

    def get(self, name: Token) -> t.Any:
        try:
            return self._map[name.lexeme]
        except KeyError:
            method = self._klass.find_method(name)
            if method is not None:
                return method.bind(self)
            raise RuntimeException(name, f"Undefined property {name.lexeme}")

    def __str__(self):
        return f"<instance of {self._klass.name}>"

    def set(self, name: Token, value: t.Any):
        self._map[name.lexeme] = value


class Class(Callable):
    @property
    def arity(self) -> int:
        init = self.find_method("init")
        if init is not None:
            return init.arity
        return 0

    def call(self, interpreter, arguments: t.List[t.Any]) -> t.Any:
        instance = ClassInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def __init__(
        self,
        name: str,
        methods: t.Dict[str, Function],
        superclass: t.Optional["Class"] = None,
    ):
        self.name = name
        self._methods = methods
        self.superclass = superclass

    def __str__(self):
        return self.name

    def find_method(self, name: t.Union[str, Token]) -> t.Optional[Function]:
        if isinstance(name, Token):
            name: str = name.lexeme
        same_class_method = self._methods.get(name)
        if same_class_method is not None:
            return same_class_method
        if self.superclass is not None:
            return self.superclass.find_method(name)
