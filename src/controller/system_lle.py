import logging
from enum import Enum

import requests
from controller.system import SystemInterface
from controller.system_lle_settings import Settings as LLEAPISettings


class LLEStatus(Enum):
    idle = "idle"
    running = "running"
    finished = "finished"
    stopped = "stopped"


class Client:
    def __init__(self, url: str):
        self.url = url

    async def get_status(self) -> dict:
        response = requests.get(f"{self.url}/status")
        return response.json()

    async def start_settling(self, settings: LLEAPISettings) -> dict:
        response = requests.post(
            f"{self.url}/startSettling", json=settings.dict(exclude={"liquid_type"})
        )
        return response.json()

    async def start_draining(self, settings: LLEAPISettings) -> dict:
        response = requests.post(
            f"{self.url}/startDraining/{settings.liquid_type.value}",
            json=settings.dict(exclude={"liquid_type"}),
        )
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
    def __init__(self, message: str = "LLE is already running"):
        super().__init__(message=message)


class LLEFailedToStartException(BaseLLEException):
    def __init__(self, message: str = "LLE failed to start"):
        super().__init__(message=message)


class LLEFailedToStopException(BaseLLEException):
    def __init__(self, message: str = "LLE failed to stop"):
        super().__init__(message=message)


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
        settings: LLEAPISettings | None = None,
    ):
        super().__init__(name, url, version)
        self.settings = settings if settings is not None else LLEAPISettings()
        self._client = Client(url)

    async def start_settling(self) -> dict:
        response = await self._set_running(self._client.start_settling)
        logging.info("LLE started settling")
        return response

    async def start_draining(self) -> dict:
        response = await self._set_running(self._client.start_draining)
        logging.info("LLE started draining")
        return response

    async def _set_running(self, client_func: callable) -> dict:
        response = await client_func(settings=self.settings)
        if response["status"] != "running":
            raise LLEFailedToStartException(
                message=f"LLE failed to start with response: {response}"
            )

        return response

    async def stop(self) -> dict:
        response = await self._client.stop()
        if response["status"] != "stopped":
            raise LLEFailedToStopException(
                message=f"LLE failed to stop with response: {response}"
            )

        logging.info("LLE stopped")

        return response

    async def get_status(self) -> LLEStatus:
        response = await self._client.get_status()
        return LLEStatus(response["status"])

    async def get_results(self) -> dict:
        return await self._client.get_results()
