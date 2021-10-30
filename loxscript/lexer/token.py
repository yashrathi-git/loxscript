from loxscript.lexer.token_type import TokenType
import typing as t


class Token:
    def __init__(self, token_type: TokenType, lexeme: str, literal: t.Any, line: int):
        # TODO: pos
        self.type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        return f"Token(type={self.type}, lexeme={self.lexeme} literal={self.literal})"
