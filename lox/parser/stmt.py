from . import expr as e
from abc import ABC, abstractmethod
from ..lexer.token import Token
import typing as t


class StmtVisitor(ABC):
    @abstractmethod
    def visit_expression_statement(self, stmt: "Expression"):
        return None

    @abstractmethod
    def visit_print_statement(self, stmt: "Print"):
        return None

    @abstractmethod
    def visit_var_statement(self, stmt: "Var"):
        return None

    @abstractmethod
    def visit_block(self, block: "Block"):
        return None


class Stmt:
    @abstractmethod
    def accept(self, visitor: StmtVisitor):
        pass


class Expression(Stmt):
    def accept(self, visitor: StmtVisitor):
        visitor.visit_expression_statement(self)

    def __init__(self, expression: e.Expr):
        self.expression = expression


class Print(Stmt):
    def accept(self, visitor: StmtVisitor):
        visitor.visit_print_statement(self)

    def __init__(self, expression: e.Expr):
        self.expression = expression


class Var(Stmt):
    def accept(self, visitor: StmtVisitor):
        visitor.visit_var_statement(self)

    def __init__(self, name: Token, initializer: e.Expr):
        self.name = name
        self.initializer = initializer


class Block(Stmt):
    def accept(self, visitor: StmtVisitor):
        visitor.visit_block(self)

    def __init__(self, statements: t.List[Stmt]):
        self.statements = statements
