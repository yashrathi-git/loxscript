import operator

from ..lexer.token import Token
from ..parser import expr as e
from ..lexer.token_type import TokenType as tt
import typing as t
from ..errors import RuntimeException


class Interpreter(e.BaseVisitor):
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
        if unary.operator == tt.BANG:
            return not self._is_truthy(right)
        if unary.operator == tt.MINUS:
            self._check_number_operands(unary.operator, right)
            return ~right

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
        elif op == tt.PLUS:
            # Because `+` could also be called on strings
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeException(op, "Operand must be number or strings")
        if op == tt.EQUAL_EQUAL:
            return self._is_equal(left, right)
        if op == tt.BANG_EQUAL:
            return not self._is_equal(left, right)

    @staticmethod
    def _check_number_operands(operator_: Token, *operands: t.Any):
        if all(isinstance(o, float) for o in operands):
            return True
        raise RuntimeException(operator_, "Operand must be a number")

    @staticmethod
    def _is_equal(a, b):
        return a == b
