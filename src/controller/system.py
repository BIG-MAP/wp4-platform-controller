from abc import ABCMeta, abstractmethod
from typing import Optional


class PollingInterface(metaclass=ABCMeta):
    def __init__(
        self,
        name: str,
        url: str,
        version: str = "0.0.0",
        settings: Optional[dict] = None,
    ):
        self.name = name
        self.url = url
        self.version = version

    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    async def stop(self):
        ...

    @abstractmethod
    async def poll(self):
        ...

    @abstractmethod
    async def poll_step(self) -> Optional[dict]:
        ...
