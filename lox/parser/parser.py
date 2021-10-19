from . import expr as e
from ..handle_errors import parse_error
from ..lexer.token import Token
import typing as t
from ..lexer.token_type import TokenType as tt
from ..errors import ParseError


class Parser:
    def __init__(self, tokens: t.List[Token]):
        self._tokens = tokens
        self._current = 0

    def _match(self, *types: tt) -> bool:
        # If `Token` have any of the given types, it consumes the `Token`
        # token will be an instance of `Token` class
        """
        Returns true if token is of any of the given types. It also consumes the Token
        """
        for type_ in types:
            if self._check(type_):
                self._advance()
                return True
        return False

    def _check(self, type_: tt):
        """
        Returns true if the current token is of the given type
        """
        # Unlike `match` it doesn't consume the token
        if self._is_at_end():
            return False
        return self._peek().type == type_

    def _advance(self):
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _previous(self):
        return self._tokens[self._current - 1]

    def _peek(self):
        return self._tokens[self._current]

    def _is_at_end(self):
        return self._peek().type == tt.EOF

    def _equality(self):
        """
        Rule:
        equality ::= comparison ( ( "!=" | "==" ) comparison )* ;
        """
        # NOTE that if parser never encounters equality operator,
        # it would never enter the while loop. In that case this method matches
        # an equality operator or anything of higher precedence
        expr: e.Expr = self._comparison()
        while self._match(tt.BANG_EQUAL, tt.EQUAL_EQUAL):
            operator: Token = self._previous()  # `Token` that was matched
            right: e.Expr = self._comparison()
            expr = e.Binary(expr, operator, right)

        return expr

    def _comparison(self):
        """
        Rule:
        comparison ::= term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
        """
        expr: e.Expr = self._term()
        while self._match(tt.GREATER_EQUAL, tt.GREATER, tt.LESS_EQUAL, tt.LESS):
            operator: Token = self._previous()
            right: e.Expr = self._term()
            expr = e.Binary(left=expr, operator=operator, right=right)
        return expr

    def _term(self):
        expr: e.Expr = self._factor()

        while self._match(tt.MINUS, tt.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = e.Binary(left=expr, right=right, operator=operator)

        return expr

    def _factor(self):
        expr: e.Expr = self._unary()

        while self._match(tt.STAR, tt.SLASH):
            operator = self._previous()
            right = self._unary()
            expr = e.Binary(expr, operator, right)

        return expr

    def _unary(self):
        while self._match(tt.BANG, tt.MINUS):
            operator = self._previous()
            right = self._unary()
            return e.Unary(operator, right)

        return self._primary()

    def _expression(self):
        return self._equality()

    def _primary(self):
        if self._match(tt.TRUE):
            return e.Literal(True)
        if self._match(tt.FALSE):
            return e.Literal(False)
        if self._match(tt.STRING, tt.NUMBER):
            return e.Literal(self._previous().literal)
        if self._match(tt.NIL):
            return e.Literal(None)
        if self._match(tt.LEFT_BRACE):
            expr = self._expression()
            self._consume(tt.RIGHT_BRACE, "Expected ')' after expression")
            return e.Grouping(expression=expr)
        raise self._error(self._peek(), "Expected expression.")

    def _consume(self, type_: tt, message: str):
        """
        It's similar to match. If the token is of given type it consumes it.
        If there is some other token, it raises an error.
        """
        if self._check(type_):
            self._advance()
            return True
        raise self._error(self._peek(), message)

    @staticmethod
    def _error(token: Token, message: str) -> ParseError:
        parse_error(token, message)
        return ParseError()

    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().type == tt.SEMICOLON:
                return

            if self._peek().type in (
                tt.CLASS,
                tt.FUNCTION,
                tt.VAR,
                tt.FOR,
                tt.IF,
                tt.WHILE,
                tt.PRINT,
                tt.RETURN,
            ):
                return

        self._advance()

    def parse(self) -> t.Optional[e.Expr]:
        try:
            return self._expression()
        except ParseError:
            return
