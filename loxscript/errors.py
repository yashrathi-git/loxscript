class RuntimeException(RuntimeError):
    def __init__(self, token, message):
        super(RuntimeException, self).__init__(message)
        self.token = token


class ParseError(Exception):
    pass


class Return(RuntimeError):
    """
    This must be handled gracefully. It's just to go behind in the call stack.
    """

    def __init__(self, value):
        super(Return, self).__init__()
        self.value = value
