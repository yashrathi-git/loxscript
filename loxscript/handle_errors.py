from .errors import RuntimeException
from .lexer.token import Token
from .lexer.token_type import TokenType as tt

_errors = {"_errors": False, "runtime_errors": False}


def report(line: int, where: str, message: str):
    print(f"[line: {line}] Error {where} : {message}")
    _errors["_errors"] = True


def update_error(runtime: bool, other_error: bool):
    _errors["_errors"] = other_error
    _errors["runtime_errors"] = runtime


def error(line: int, error_message: str):
    report(line, "", error_message)


def parse_error(token: Token, message: str):
    if token.type == tt.EOF:
        report(token.line, "at end", message)
    else:
        report(token.line, f"at {token.lexeme}", message)


def runtime_error(runtime_exception: RuntimeException):
    print(str(runtime_exception) + f"\n[line: {runtime_exception.token.line}]")
    _errors["runtime_errors"] = True


def has_error():
    return _errors["_errors"]


def has_runtime_error():
    return _errors["runtime_errors"]


def has_any_error():
    return any(_errors.values())
