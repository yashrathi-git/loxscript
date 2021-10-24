import operator

from .callable import Callable, Function
from .environment import Environment
from ..handle_errors import runtime_error
from ..lexer.token import Token
from ..parser import expr as e
from ..lexer.token_type import TokenType as tt
import typing as t
from ..errors import RuntimeException, Return
from ..parser import stmt
from .natives import Clock


class Interpreter(e.BaseVisitor, stmt.StmtVisitor):
    def visit_return_statement(self, return_stmt: stmt.Return):
        value = None
        if return_stmt.value is not None:
            value = self._evaluate(return_stmt.value)
        raise Return(value)

    def visit_function(self, func_stmt: stmt.Function):
        function = Function(func_stmt, self._environment)
        self._environment.define(func_stmt.name.lexeme, function)

    def visit_call_expr(self, call: e.Call):
        # This would evaluate it as a variable and give us `Callable` class object
        # if not it's not a callable object
        callee = self._evaluate(call.callee)
        args = []
        for arg in call.arguments:
            args.append(self._evaluate(arg))
        if not isinstance(callee, Callable):
            raise RuntimeException(call.paren, "Object is not callable")
        function: Callable = callee
        if function.arity != len(args):
            raise RuntimeException(
                call.paren, f"Expected {function.arity} arguments but got {len(args)}"
            )
        # Because the function call itself is an expression, we are just able to return
        # the value.
        return function.call(self, args)

    def visit_logical(self, logical: e.Logical):
        left = self._evaluate(logical.left)
        op = logical.operator.type

        # We don't evaluate right unless we need to
        if op == tt.OR:
            if self._is_truthy(left):
                return left
        elif op == tt.AND:
            if not self._is_truthy(left):
                return left

        return self._evaluate(logical.right)

    def visit_if_statement(self, if_stmt: stmt.If):
        if self._is_truthy(self._evaluate(if_stmt.condition)):
            self._execute(if_stmt.then_branch)
        elif if_stmt.else_branch is not None:
            self._execute(if_stmt.else_branch)

    def __init__(self):
        self.globals = Environment()
        self._environment = self.globals
        self.globals.define("clock", Clock())
        self._locals: t.Dict[e.Expr, int] = {}

    def visit_assign(self, assignment: e.Assign):
        value = self._evaluate(assignment.value)
        distance = self._locals.get(assignment)
        if distance is not None:
            self._environment.assign_at(distance, assignment.name, value)
        else:
            self.globals.assign(assignment.name, value)
        self._environment.assign(name=assignment.name, value=value)
        return value

    def visit_var_statement(self, var_stmt: stmt.Var):
        """
        Visitor for variable declaration statement
        """
        value = None
        if var_stmt.initializer is not None:
            # Evaluate the ast class, and get python object as value
            value = self._evaluate(var_stmt.initializer)
        self._environment.define(name=var_stmt.name.lexeme, value=value)

    def visit_variable_expr(self, var: e.Variable):
        return self.look_up_variable(var.name, var)

    def look_up_variable(self, name: Token, var: e.Expr):
        dist = self._locals.get(var)
        if dist is not None:
            return self._environment.get_at(dist, name.lexeme)
        return self.globals.get(name)

    def visit_expression_statement(self, expr_stmt: stmt.Expression):
        self._evaluate(expr_stmt.expression)

    def visit_print_statement(self, print_stmt: stmt.Print):
        value = self._evaluate(print_stmt.expression)
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
        self.execute_block(block.statements, Environment(self._environment))

    def execute_block(self, statements: t.List[stmt.Stmt], environment: Environment):
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

    def _execute(self, st: stmt.Stmt):
        st.accept(self)

    def interpret(self, statements: t.List[stmt.Stmt]):
        try:
            for st in statements:
                self._execute(st)
        except RuntimeException as err:
            runtime_error(err)

    def visit_while_statement(self, while_stmt: stmt.While):
        while self._is_truthy(self._evaluate(while_stmt.condition)):
            self._execute(while_stmt.block)

    def resolve(self, expr: e.Expr, depth: int):
        self._locals[expr] = depth
