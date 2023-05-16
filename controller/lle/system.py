import logging
from enum import Enum

from controller.lle.client import Client
from controller.lle.exceptions import (
    LLEFailedToStartException,
    LLEFailedToStopException,
)
from controller.system import SystemInterface
from controller.lle.settings import Settings


class LLEStatus(Enum):
    idle = "idle"
    running = "running"
    finished = "finished"
    stopped = "stopped"


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
        settings: Settings | None = None,
    ):
        super().__init__(name, url, version)
        self.settings = settings if settings is not None else Settings()
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
