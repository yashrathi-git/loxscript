import typing as t

from loxscript.handle_errors import error
from loxscript.lexer.token import Token
from loxscript.lexer.token_type import TokenType as tt


class Scanner:
    def __init__(self, source: str):
        self._tokens = []
        self._source = source
        # The start field points to the first character
        # in the lexeme being scanned
        self._start = 0
        # current points at the character currently being considered.
        self._current = 0
        self._line = 1

    def _is_at_end(self, at_idx: t.Optional[int] = None):
        if not at_idx:
            at_idx = self._current
        # The `self._current` should always be one idx pos ahead of what we are
        # currently scanning
        return at_idx >= len(self._source)

    def _advance(self):
        return_val = self._source[self._current]
        self._current += 1
        return return_val

    def _peek(self, more: int = 0):
        f_idx = self._current + more
        if self._is_at_end(f_idx):
            return r"\0"
        return self._source[f_idx]

    def _handle_strings(self, start_delimiter: str):
        while (not self._peek() == start_delimiter) and (not self._is_at_end()):
            if self._peek() == "\n":
                self._line += 1
            self._advance()
        if self._is_at_end():
            error(self._line, "Unterminated string")
            return

        # Closing " or '
        self._advance()
        # Not include the delimiters
        value = self._source[self._start + 1 : self._current - 1]
        self._add_token(tt.STRING, value)

    def _handle_numbers(self):
        while self._peek().isdigit():
            self._advance()

        # We look after after the peeked '.', because we don't want to consume '.'
        # until we are sure there is a number behind it
        # '.' without number case is already handled by `_get_token`
        if self._peek() == "." and self._peek(1).isdigit():
            # Consume the '.'
            self._advance()
            while self._peek().isdigit():
                self._advance()
        self._add_token(tt.NUMBER, float(self._source[self._start : self._current]))

    def _handle_identifiers(self):
        _keywords = [
            tt.WHILE,
            tt.FOR,
            tt.IF,
            tt.ELSE,
            tt.FOR,
            tt.FUNCTION,
            tt.PRINT,
            tt.SUPER,
            tt.RETURN,
            tt.VAR,
            tt.TRUE,
            tt.FALSE,
            tt.CLASS,
            tt.AND,
            tt.OR,
            tt.NIL,
            tt.THIS,
        ]
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        value = self._source[self._start : self._current]
        type_ = tt.IDENTIFIER
        if self._safe_to_token_type(value) in _keywords:
            type_ = tt(value)

        self._add_token(type_)

    @staticmethod
    def _safe_to_token_type(st):  # Doesn't raise ValueError returns `None` instead
        try:
            token = tt(st)
        except ValueError:
            return None
        return token

    def _get_token(self):
        char = self._advance()
        add = self._add_token
        single_char_tokens = [
            tt.LEFT_PAREN,
            tt.RIGHT_PAREN,
            tt.LEFT_BRACE,
            tt.RIGHT_BRACE,
            tt.COMMA,
            tt.DOT,
            tt.MINUS,
            tt.PLUS,
            tt.SEMICOLON,
            tt.STAR,
        ]
        if char.isspace():
            if char == "\n":
                self._line += 1
        elif self._safe_to_token_type(char) in single_char_tokens:
            add(tt(char))
        elif char == ">":
            add(tt.GREATER_EQUAL if self._match("=") else tt.GREATER)
        elif char == "!":
            add(tt.BANG_EQUAL if self._match("=") else tt.BANG)
        elif char == "<":
            add(tt.LESS_EQUAL if self._match("=") else tt.LESS)
        elif char == "=":
            add(tt.EQUAL_EQUAL if self._match("=") else tt.EQUAL)
        elif char == "/":
            if self._match("/"):
                while (not self._peek() == "\n") and (not self._is_at_end()):
                    self._advance()
            else:
                self._add_token(tt.SLASH)
        elif char in ('"', "'"):
            self._handle_strings(char)
        elif char.isdigit():
            self._handle_numbers()
        elif char.isalnum() or char == "_":
            self._handle_identifiers()
        else:
            error(self._line, f"Illegal character {char}")

    def get_tokens(self):
        while not self._is_at_end():
            self._start = self._current
            self._get_token()

        self._tokens.append(Token(tt.EOF, "", None, self._line))
        return self._tokens

    def _match(self, expected: str) -> bool:

        if self._is_at_end():
            return False
        if not self._source[self._current] == expected:
            return False
        self._current += 1
        return True

    def _add_token(self, t_type: tt, t_literal: t.Optional[t.Any] = None):
        # Raw lexeme
        text = self._source[self._start : self._current]
        self._tokens.append(Token(t_type, text, t_literal, self._line))
