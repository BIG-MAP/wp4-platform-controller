import asyncio
import logging
from enum import Enum

from controller.system_lle import LLEStatus, LLESystem
from controller.system_plc import PLCSystem


class Status(Enum):
    idle = "idle"
    running = "running"
    stopped = "stopped"


class RootController:
    """
    RootController is the main controller responsible for communication between all underlying systems.
    It starts and stops the underlying systems, and polls them for status updates periodically.
    """

    def __init__(self, plc: PLCSystem, lle: LLESystem, polling_interval: int = 5):
        self.plc = plc
        self.lle = lle
        self.polling_interval = polling_interval
        self.status = Status.idle

    async def start(self):
        self.status = Status.running
        logging.info("Root controller started")

    async def stop(self):
        self.status = Status.stopped
        logging.info("Root controller stopped")

    async def get_status(self) -> Status:
        return self.status

    async def get_system_statuses(self) -> dict:
        return {
            self.plc.name: None,
            self.lle.name: await self.lle.get_status(),
        }

    async def poll(self):
        logging.info("Starting root controller polling")

        previous_lle_status = None

        while True:
            if self.status != Status.running:
                self._stop_systems()
                break

            # launching underlying systems

            should_start = await self.plc.should_start()
            logging.debug("Should start: %s", should_start)

            if should_start:
                response = await self.lle.start()
                logging.debug("LLE response: %s", response)

                # switching PLC to started=False so we don't start the LLE again
                await self.plc.set_is_started(False)

            lle_status = await self.lle.get_status()
            lle_results = None

            if (
                previous_lle_status == LLEStatus.running
                and lle_status == LLEStatus.finished
            ):
                lle_results = await self.lle.get_results()

            if lle_results is not None:
                # TODO: PLC server must support results
                # await self.plc.set_lle_results(lle_results)
                logging.debug("LLE results: %s", lle_results)

            if lle_status != previous_lle_status:
                await self.plc.set_lle_status(lle_status.value)
                logging.debug("LLE status changed to: %s", lle_status)
                previous_lle_status = lle_status

            await asyncio.sleep(self.polling_interval)

    async def _stop_systems(self):
        logging.info("Stopping root controller underlying systems")

        self.lle.stop()
        lle_status = await self.lle.get_status()

        await self.plc.set_lle_status(lle_status.value)

        # TODO: PLC server must support results
        # lle_results = await self.lle.get_results()
        # if lle_results is not None:
        #     await self.plc.set_lle_results(lle_results)
