class RuntimeException(RuntimeError):
    def __init__(self, token, message):
        super(RuntimeException, self).__init__(message)
        self.token = token


class ParseError(Exception):
    pass
