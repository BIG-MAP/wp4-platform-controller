import asyncio
import logging
from enum import Enum
from typing import Optional

import requests
from controller.system import PollingInterface


class APIStatus(Enum):
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

    async def start(self, settings: Optional[dict] = None) -> dict:
        if settings is None:
            settings = {"sleep_delay": 30}

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


class LLESystem(PollingInterface):
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
        settings: dict | None = None,
        polling_interval: int = 5,
    ):
        super().__init__(name, url, version)
        self.polling_interval = polling_interval
        self._client = Client(url)
        self._is_running = False

    async def start(self) -> dict:
        if self._is_running:
            raise LLERunningException()

        response = await self._client.start()
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

    async def poll(self):
        while True:
            if not self._is_running:
                logging.info("LLE stopped. Stop polling")
                break

            status = await self.get_status()

            if status["status"] == APIStatus.finished.value:
                self._is_running = False
                results = await self._client.get_results()
                # TODO: send results to PLC
                logging.info("Received LLE results. Stop polling")
                break
            elif status["status"] == APIStatus.stopped.value:
                self._is_running = False
                logging.info("LLE stopped. Stop polling")
                break
            elif status["status"] == APIStatus.idle.value:
                logging.info("LLE has not started yet. Stop polling")
                break

            await asyncio.sleep(self.polling_interval)

    async def poll_step(self) -> Optional[dict]:
        status = await self.get_status()

        if status["status"] == APIStatus.finished.value:
            self._is_running = False
            results = await self._client.get_results()
            logging.debug("Received LLE results. Stop polling")
            return results
        elif status["status"] == APIStatus.stopped.value:
            self._is_running = False
            logging.debug("LLE stopped. Stop polling")
        elif status["status"] == APIStatus.idle.value:
            self._is_running = False
            logging.debug("LLE has not started yet. Stop polling")

        return None

    async def get_status(self) -> dict:
        return await self._client.get_status()
