# Loxscript
Python port of the book [crafting interpreters](http://craftinginterpreters.com/)
with some of my own changes and additions.

## Features and quick tutorial
[You could find the tutorial here](https://github.com/yashrathi-git/loxscript/blob/main/snippets.md)

## Requirements
* python >= 3.8

## Installation
### Install with pip

```sh
$ pip install git+https://github.com/yashrathi-git/loxscript
```
Now you could run `loxscript` to access the interpreter.

If you are doing user install, you must add the user-level `bin` directory to your `PATH` environment variable in order to use loxscript. If you are using a Unix derivative (FreeBSD, GNU / Linux, OS X), you can achieve this by using `export PATH="$HOME/.local/bin:$PATH"` command.

**Usage:**
```sh
$ loxscript                             # Starts a loxscript repl
$ loxscript path/to/source_code.ls      # Executes the file
```
### Without pip
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
- [ ] ADD TESTS!
- [ ] Support for multiline comments
- [x] Complete classes and inheritance part
- [ ] Lists and Dicts
- [ ] Lambdas
- [ ] Provide builtins to do web-requests
- [x] Add `setup.py` for direct install
- [ ] **Add support for decorators**
- [ ] Add more builtins with decorators like `@property`, `@classmethod` etc.

