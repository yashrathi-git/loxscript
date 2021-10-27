# Loxscript
Python implementation of the book [crafting interpreters](http://craftinginterpreters.com/). It's a tree-walk intereter.

## Requirements
* python >= 3.8

## Running the interpreter
1. Clone the repo
    ```sh
    $ git clone https://github.com/yashrathi-git/loxscript
    ```
2. Navigate to source code directory.
    ```sh
    $ cd loxscript
    ```
3. Running(*Make sure you are in the source code directory*):
    ```sh
    $ python run.py                           # Starts a loxscript repl
    $ python run.py path/to/source_code.ls    # Executes the file
    ```

## TODO:
- [ ] Complete classes and inheritance part
- [ ] Better errors(with arrow pointer where approximately it's in the line)
- [ ] Lists and Dicts
- [ ] Lambdas
- [ ] Provide builtins to do web-requests
- [ ] Add `setup.py` for direct install

