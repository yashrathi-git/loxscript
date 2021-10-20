import operator

from .environment import Environment
from ..handle_errors import runtime_error
from ..lexer.token import Token
from ..parser import expr as e
from ..lexer.token_type import TokenType as tt
import typing as t
from ..errors import RuntimeException
from ..parser import stmt


class Interpreter(e.BaseVisitor, stmt.StmtVisitor):
    def __init__(self):
        self._environment = Environment()

    def visit_assign(self, assignment: e.Assign):
        value = self._evaluate(assignment.value)
        self._environment.assign(name=assignment.name, value=value)
        return value

    def visit_var_statement(self, stmt: stmt.Var):
        """
        Visitor for variable declaration statement
        """
        value = None
        if stmt.initializer is not None:
            # Evaluate the ast class, and get python object as value
            value = self._evaluate(stmt.initializer)
        self._environment.define(name=stmt.name.lexeme, value=value)

    def visit_variable_expr(self, var: e.Variable):
        return self._environment.get(var.name)

    def visit_expression_statement(self, stmt: stmt.Expression):
        self._evaluate(stmt.expression)

    def visit_print_statement(self, stmt: stmt.Print):
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def _evaluate(self, expr: e.Expr):
        return expr.accept(self)

    def visit_grouping(self, grouping: e.Grouping):
        return self._evaluate(grouping.expression)

    @staticmethod
    def _is_truthy(val: t.Any) -> bool:
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        return val

    def visit_unary_method(self, unary: e.Unary):
        right = self._evaluate(unary.right)
        if unary.operator.type == tt.BANG:
            return not self._is_truthy(right)
        if unary.operator.type == tt.MINUS:
            self._check_number_operands(unary.operator, right)
            return ~int(right)

        # Unreachable
        return None

    def visit_literal_expr(self, literal: e.Literal):
        return literal.value

    def visit_binary(self, binary: e.Binary):
        left = self._evaluate(binary.left)
        right = self._evaluate(binary.right)

        op = binary.operator

        operator_map = {
            "-": operator.sub,
            "/": operator.truediv,
            "*": operator.mul,
            ">": operator.gt,
            ">=": operator.ge,
            "<": operator.lt,
            "<=": operator.le,
        }

        if op.lexeme in operator_map.keys():
            self._check_number_operands(op, left, right)
            return operator_map[op.lexeme](float(left), float(right))
        elif op.type == tt.PLUS:
            # Because `+` could also be called on strings
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeException(op, "Operand must be number or strings")
        if op.type == tt.EQUAL_EQUAL:
            return self._is_equal(left, right)
        if op.type == tt.BANG_EQUAL:
            return not self._is_equal(left, right)

    def visit_block(self, block: stmt.Block):
        self._execute_block(block.statements, Environment(self._environment))

    def _execute_block(self, statements: t.List[stmt.Stmt], environment: Environment):
        """
        Uses a new lexical environment to execute the block.
        After execution it resets the environment, to previous one.
        """
        previous = self._environment
        try:
            self._environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = previous

    @staticmethod
    def _check_number_operands(operator_: Token, *operands: t.Any):
        if all(isinstance(o, float) for o in operands):
            return True
        raise RuntimeException(operator_, "Operand must be a number")

    @staticmethod
    def _is_equal(a, b):
        return a == b

    @staticmethod
    def _stringify(obj: t.Any):
        if obj is None:
            return "nil"
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        if isinstance(obj, bool):
            return str(obj).lower()
        return str(obj)

    def interpret(self, statements: t.List[stmt.Stmt]):
        try:
            for st in statements:
                self._execute(st)
        except RuntimeException as err:
            runtime_error(err)

    def _execute(self, st: stmt.Stmt):
        st.accept(self)
