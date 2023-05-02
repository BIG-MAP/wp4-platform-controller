from abc import ABCMeta


class SystemInterface(metaclass=ABCMeta):
    def __init__(
        self,
        name: str,
        url: str,
        version: str = "0.0.0",
    ):
        self.name = name
        self.url = url
        self.version = version
