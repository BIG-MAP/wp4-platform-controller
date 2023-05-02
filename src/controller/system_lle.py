import logging
from dataclasses import dataclass
from enum import Enum

import requests
from controller.system import SystemInterface


class LLEStatus(Enum):
    idle = "idle"
    running = "running"
    finished = "finished"
    stopped = "stopped"


@dataclass
class LLESettings:
    sleep_delay: int


class Client:
    def __init__(self, url: str):
        self.url = url

    async def get_status(self) -> dict:
        response = requests.get(f"{self.url}/status")
        return response.json()

    async def start(self, settings: dict) -> dict:
        response = requests.post(f"{self.url}/start", json=settings)
        return response.json()

    async def stop(self) -> dict:
        response = requests.post(f"{self.url}/stop")
        return response.json()

    async def get_results(self) -> dict:
        response = requests.get(f"{self.url}/results")
        return response.json()


class BaseLLEException(Exception):
    def __init__(self, message: str):
        self.message = message


class LLERunningException(BaseLLEException):
    def __init__(self):
        super().__init__("LLE is already running")


class LLEFailedToStartException(BaseLLEException):
    def __init__(self):
        super().__init__("LLE failed to start")


class LLEFailedToStopException(BaseLLEException):
    def __init__(self):
        super().__init__("LLE failed to stop")


class LLESystem(SystemInterface):
    """
    LLESystem is a class responsible for interacting with the LLE system. LLE stands for Liquid-Liquid Extraction.
    LLE should be started when there is a start command on PLC. After that, LLE gets polled periodically for a status,
    and when it's done, it queries the results and sends them to the PLC.
    """

    def __init__(
        self,
        name: str,
        url: str,
        version: str = "0.0.0",
        settings: LLESettings | None = None,
    ):
        super().__init__(name, url, version)
        self.settings = settings if settings is not None else LLESettings(30)
        self._client = Client(url)
        self._is_running = False

    async def start(self) -> dict:
        if self._is_running:
            raise LLERunningException()

        response = await self._client.start(self.settings.__dict__)
        if response["status"] != "running":
            raise LLEFailedToStartException()

        logging.info("LLE started")

        self._is_running = True

        return response

    async def stop(self) -> dict:
        self._is_running = False

        response = await self._client.stop()
        if response["status"] != "stopped":
            raise LLEFailedToStopException()

        logging.info("LLE stopped")

        return response

    async def get_status(self) -> LLEStatus:
        response = await self._client.get_status()
        return LLEStatus(response["status"])

    async def get_results(self) -> dict:
        return await self._client.get_results()
