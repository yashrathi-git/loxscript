import sys
from pathlib import Path
from pprint import pprint

from lox.lexer.scanner import Scanner
from lox.parser.parser import Parser
from .handle_errors import has_any_error, update_error


def run(source):
    token_list = Scanner(source=source).get_tokens()
    parser = Parser(token_list)
    pprint(parser.parse())


def run_repl():
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
    run(source=code)

    if has_any_error():
        sys.exit(1)


def main():
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
