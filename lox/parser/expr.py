from ..lexer.token import Token
import typing as t
from abc import ABC, abstractmethod


class BaseVisitor(ABC):
    @abstractmethod
    def visit_binary(self, binary: "Binary"):
        pass

    @abstractmethod
    def visit_grouping(self, grouping: "Grouping"):
        pass

    @abstractmethod
    def visit_unary_method(self, unary: "Unary"):
        pass

    @abstractmethod
    def visit_literal_expr(self, literal: "Literal"):
        pass

    @abstractmethod
    def visit_variable_expr(self, var: "Variable"):
        pass

    @abstractmethod
    def visit_assign(self, assignment: "Assign"):
        pass

    @abstractmethod
    def visit_logical(self, logical: "Logical"):
        pass

    @abstractmethod
    def visit_call_expr(self, call: "Call"):
        pass


class Expr(ABC):
    """
    Class for expressions
    """

    @abstractmethod
    def accept(self, visitor: BaseVisitor) -> t.Any:
        pass


class Binary(Expr):
    def accept(self, visitor: BaseVisitor) -> t.Any:
        return visitor.visit_binary(self)

    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.right = right
        self.operator = operator

    def __repr__(self):
        return f"({self.left} {self.operator.lexeme} {self.right})"


class Grouping(Expr):
    def accept(self, visitor: BaseVisitor) -> t.Any:
        return visitor.visit_grouping(self)

    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self):
        return f"group({self.expression})"


class Literal(Expr):
    def accept(self, visitor: BaseVisitor) -> t.Any:
        return visitor.visit_literal_expr(self)

    def __init__(self, value: t.Any):
        self.value = value

    def __repr__(self):
        return f"{self.value}"


class Unary(Expr):
    def accept(self, visitor: BaseVisitor) -> t.Any:
        return visitor.visit_unary_method(self)

    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"({self.operator.lexeme}{self.right})"


class Variable(Expr):
    def accept(self, visitor: BaseVisitor) -> t.Any:
        return visitor.visit_variable_expr(self)

    def __init__(self, name: Token):
        self.name = name


class Assign(Expr):
    def accept(self, visitor: BaseVisitor) -> t.Any:
        return visitor.visit_assign(self)

    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: BaseVisitor) -> t.Any:
        return visitor.visit_logical(self)


class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: t.List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: BaseVisitor) -> t.Any:
        return visitor.visit_call_expr(self)
