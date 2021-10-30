from enum import Enum


class TokenType(Enum):
    # Single - character
    LEFT_PAREN = "{"
    RIGHT_PAREN = "}"
    LEFT_BRACE = "("
    RIGHT_BRACE = ")"
    COMMA = ","
    DOT = "."
    MINUS = "-"
    PLUS = "+"
    SEMICOLON = ";"
    SLASH = "/"
    STAR = "*"

    BANG = "!"
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="

    IDENTIFIER = "identifier"
    STRING = "string"
    NUMBER = "number"

    ELSE = "else"
    CLASS = "class"
    IF = "if"
    PRINT = "print"
    FOR = "for"
    RETURN = "return"
    SUPER = "super"
    FUNCTION = "fun"
    AND = "and"
    VAR = "var"
    WHILE = "while"
    OR = "or"
    TRUE = "true"
    FALSE = "false"
    NIL = "nil"

    EOF = None
    THIS = "this"
