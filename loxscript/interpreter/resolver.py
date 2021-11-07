from contextlib import contextmanager, ExitStack
from enum import Enum, auto

from .interpreter import Interpreter
from ..lexer.token import Token
from ..parser import stmt as stmt  # to prevent shadowing stmt parameter
from ..parser import expr as e
from ..handle_errors import parse_error
from functools import singledispatchmethod
import typing as t


class FunctionType(Enum):
    FUNCTION = auto()
    NONE = auto()
    METHOD = auto()
    INITIALIZER = auto()


class ClassType(Enum):
    CLASS = auto()
    SUBCLASS = auto()
    NONE = auto()


class Resolver(e.BaseVisitor, stmt.StmtVisitor):
    def visit_super_expr(self, super_expr: e.Super):
        if self._current_class is ClassType.NONE:
            parse_error(super_expr.keyword, "Cannot use 'super' outside a class.")
        if not self._current_class == ClassType.SUBCLASS:
            parse_error(super_expr.keyword, "Cannot use 'super' with no subclass.")
        self._resolve_local(super_expr, super_expr.keyword)

    def visit_set_expr(self, set_expr: e.Set):
        # Value is the value of the variable
        self.resolve(set_expr.value)
        # Object is, ex in `a.b.c`, `a.b` is the object and `c` is the name
        # `c` might not exist yet because we can dynamically set those
        self.resolve(set_expr.object)

    def visit_get_expr(self, get_expr: e.Get):
        self.resolve(get_expr.object)

    def visit_class_statement(self, class_stmt):
        enclosing_class = self._current_class
        self._current_class = ClassType.CLASS
        self._declare(class_stmt.name)
        self._define(class_stmt.name)

        if (class_stmt.superclass is not None) and (
            class_stmt.name.lexeme == class_stmt.superclass.name.lexeme
        ):
            parse_error(class_stmt.name, "A class cannot inherit from itself.")

        with ExitStack() as stack:
            if class_stmt.superclass is not None:
                self._current_class = ClassType.SUBCLASS
                self.resolve(class_stmt.superclass)
                # we start new scope after we have resolved the superclass
                stack.enter_context(self._new_scope())
                self._scopes[-1]["super"] = True

            stack.enter_context(self._new_scope())

            # `this` is treated like a variable in the enclosing scope
            self._scopes[-1]["this"] = True
            for method in class_stmt.methods:
                self._resolve_function(
                    method, FunctionType.METHOD
                )  # this also start create a new scope just for the method

        self._current_class = enclosing_class

    def __init__(self, interpreter: Interpreter):
        self._interpreter = interpreter
        self._scopes: t.List[t.Dict[str, bool]] = []
        self._current_function: FunctionType = FunctionType.NONE
        self._current_class: ClassType = ClassType.NONE

    def visit_print_statement(self, print_stmt: stmt.Print):
        self.resolve(print_stmt.expression)

    def visit_var_statement(self, var_stmt: stmt.Var):
        self._declare(var_stmt.name)
        if var_stmt.initializer is not None:
            self.resolve(var_stmt.initializer)
        self._define(var_stmt.name)

    def _declare(self, name: Token):
        if not len(self._scopes):
            return
        scope = self._scopes[-1]
        if name.lexeme in scope.keys():
            parse_error(name, f"{name.lexeme} already exists.")
        scope[name.lexeme] = False

    def _define(self, name: Token):
        if not len(self._scopes):
            return
        self._scopes[-1][name.lexeme] = True

    def visit_block(self, block: stmt.Block):
        with self._new_scope():
            self.resolve(block.statements)

    def _start_scope(self):
        self._scopes.append({})

    def _end_scope(self):
        self._scopes.pop()

    @singledispatchmethod
    def resolve(self, arg) -> None:
        """
        This doesn't need to return any data as it stores the data in the `Interpreter`
        instance itself
        """
        raise NotImplementedError(f"Unexpected type provided.")

    @resolve.register(list)
    def _(self, arg: t.List[stmt.Stmt]):
        for statement in arg:
            self.resolve(statement)

    @resolve.register(stmt.Stmt)
    def _(self, arg: stmt.Stmt):
        arg.accept(self)

    @resolve.register(e.Expr)
    def _(self, arg: e.Expr):
        arg.accept(self)

    def visit_if_statement(self, if_stmt: stmt.If):
        self.resolve(if_stmt.condition)
        self.resolve(if_stmt.then_branch)
        if if_stmt.else_branch is not None:
            self.resolve(if_stmt.else_branch)

    def visit_while_statement(self, while_stmt: stmt.While):
        self.resolve(while_stmt.condition)
        self.resolve(while_stmt.block)

    def visit_function(self, func_stmt: stmt.Function):
        self._declare(func_stmt.name)
        self._define(func_stmt.name)

        if func_stmt.name.lexeme == "init":
            self._current_function = FunctionType.INITIALIZER

        self._resolve_function(func_stmt, FunctionType.FUNCTION)

    def visit_return_statement(self, return_stmt: stmt.Return):
        if self._current_function == FunctionType.NONE:
            parse_error(
                return_stmt.keyword, "Cannot use return outside of functions or methods"
            )
        if (return_stmt.value is not None) and (
            self._current_function == FunctionType.INITIALIZER
        ):  # we still allow empty returns in initializers `return;`
            parse_error(
                return_stmt.keyword, "Cannot return a value from an initializer"
            )
        if return_stmt.value is not None:
            self.resolve(return_stmt.value)

    def visit_expression_statement(self, expr_stmt: stmt.Expression):
        self.resolve(expr_stmt.expression)

    def visit_binary(self, binary: e.Binary):
        self.resolve(binary.left)
        self.resolve(binary.right)

    def visit_grouping(self, grouping: e.Grouping):
        self.resolve(grouping.expression)

    def visit_unary_method(self, unary: e.Unary):
        self.resolve(unary.right)

    def visit_literal_expr(self, literal: e.Literal):
        return None

    def visit_variable_expr(self, var: e.Variable):
        """
        This is the main method that kindof uploads the resolved variable information to,
        interpreter instance. It calls `resolve_local` which tells the interpreter the
        variable and its distance from the current scope.
        Ex: if it's current scope distance would be 0, 1 in the enclosing one and so on...

        The interpreter then only looks at that distance from current scope or in the
        global scope to find the value of the referenced variable.

        Even function, method or classes are just variable that are callable.
        """
        if len(self._scopes) != 0 and (self._scopes[-1].get(var.name.lexeme) is False):
            parse_error(
                var.name, "Can't read the local variable in it's own initializer"
            )
        self._resolve_local(var, var.name)

    def visit_assign(self, assignment: e.Assign):
        self.resolve(assignment.value)
        self._resolve_local(assignment, assignment.name)

    def visit_logical(self, logical: e.Logical):
        self.resolve(logical.left)
        self.resolve(logical.right)

    def visit_call_expr(self, call: e.Call):
        self.resolve(call.callee)
        for arg in call.arguments:
            self.resolve(arg)

    def _resolve_local(self, expr: e.Expr, name: Token):
        """
        Tells the interpreter about the distance of the referenced var from the current
        scope
        """
        for idx, scope in enumerate(reversed(self._scopes)):
            if name.lexeme in scope.keys():
                # we pass the number of scope between the current scope and the scope
                # in which the variable was found. If it were find in the current scope
                # it's 0
                self._interpreter.resolve(expr, idx)
                return

    @contextmanager
    def _new_scope(self):
        self._start_scope()
        yield
        self._end_scope()

    def _resolve_function(self, function: stmt.Function, type_: FunctionType):
        enclosing_func = self._current_function
        self._current_function = type_
        with self._new_scope():
            for param in function.params:
                self._declare(param)
                self._define(param)
            self.resolve(function.body)
        self._current_function = enclosing_func

    def visit_this_expr(self, this_expr: e.This):
        if self._current_class == ClassType.NONE:
            parse_error(this_expr.keyword, "Cannot use 'this' outside of a class")
            return

        self._resolve_local(this_expr, this_expr.keyword)
