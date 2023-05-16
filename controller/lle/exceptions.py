class BaseLLEException(Exception):
    def __init__(self, message: str):
        self.message = message


class LLERunningException(BaseLLEException):
    def __init__(self, message: str = "LLE is already running"):
        super().__init__(message=message)


class LLEFailedToStartException(BaseLLEException):
    def __init__(self, message: str = "LLE failed to start"):
        super().__init__(message=message)


class LLEFailedToStopException(BaseLLEException):
    def __init__(self, message: str = "LLE failed to stop"):
        super().__init__(message=message)
