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

    @abstractmethod
    def visit_if_statement(self, stmt: "If"):
        return None

    @abstractmethod
    def visit_while_statement(self, stmt: "While"):
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


class If(Stmt):
    def accept(self, visitor: StmtVisitor):
        visitor.visit_if_statement(self)

    def __init__(self, condition: e.Expr, then_branch: Stmt, else_branch: Stmt):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class While(Stmt):
    def accept(self, visitor: StmtVisitor):
        return visitor.visit_while_statement(self)

    def __init__(self, condition: e.Expr, block: Stmt):
        self.condition = condition
        self.block = block
