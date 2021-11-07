import sys
import typing as t
from pathlib import Path

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
    print("-------------Lox REPL--------------")
    print("Press `Ctrl+D` to exit")
    print(
        "If you want to use multi-line code-block({ }) \n"
        "then use `{` at the end the line only "
        "to continue the line.\n"
        "Similarly use `}` at end of the line to exit the block.\n"
    )
    while True:
        try:
            code = input("> ")
            if code.endswith("{"):
                while not code.endswith("}"):
                    code += input("(block)>> ")
            run(code)
            update_error(False, False)

        except EOFError:
            print("\nExiting")
            break
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")


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
