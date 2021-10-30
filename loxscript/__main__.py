import sys
from pathlib import Path
import typing as t

from loxscript.interpreter.resolver import Resolver
from loxscript.lexer.scanner import Scanner
from loxscript.parser.parser import Parser
from .handle_errors import has_any_error, update_error
from .interpreter.interpreter import Interpreter


class App:
    def __init__(self):
        self._interpreter = Interpreter()

    def __call__(self, source):
        token_list = Scanner(source=source).get_tokens()
        statements = Parser(token_list).parse()
        if has_any_error():
            return
        resolver = Resolver(self._interpreter)
        resolver.resolve(statements)
        if has_any_error():
            return

        self._interpreter.interpret(statements)


def run_repl():
    run = App()
    while True:
        try:
            code = input("> ")
            run(code)
            update_error(False, False)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting")
            break


def run_file(fp: str):
    code = Path(fp).read_text()
    run = App()
    run(source=code)

    if has_any_error():
        sys.exit(1)


def main(
    args: t.Optional[t.List[str]] = None,
):  # For debugging purposes, args could be provided directly
    if not args:
        args = sys.argv
    if len(args) > 2:
        print("Usage: pylox SCRIPT")
        sys.exit(1)
    if len(args) == 2:
        run_file(args[1])
    else:
        run_repl()


if __name__ == "__main__":
    main()
