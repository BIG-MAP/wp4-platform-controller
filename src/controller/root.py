import logging
from typing import List, Optional

from controller.system import PollingInterface


class RootController:
    def __init__(self, systems: List[PollingInterface] = []):
        self._validate_systems_list(systems)
        self.systems = systems
        self._is_running = False

    def _validate_systems_list(self, systems: List[PollingInterface]):
        names = []
        urls = []

        for system in systems:
            if system.name in names:
                raise Exception("Duplicate system name")
            if system.url in urls:
                raise Exception("Duplicate system url")
            names.add(system.name)
            urls.add(system.url)

    def get_systems(self) -> List[dict]:
        return self.systems

    def get_system(self, name: str) -> Optional[PollingInterface]:
        for system in self.systems:
            if system.name == name:
                return system
        return None

    def add_system(self, system: PollingInterface):
        self.systems.append(system)

    def remove_system(self, system: PollingInterface):
        self.systems.remove(system)

    async def start(self) -> List[dict]:
        responses = []

        for system in self.systems:
            response = await system.start()
            responses.append(response)

        self._is_running = True

        return responses

    async def stop(self) -> List[dict]:
        self._is_running = False

        responses = []

        for system in self.systems:
            response = await system.stop()
            responses.append(response)

        return responses

    async def poll(self):
        lle_system = self.get_system("LLE")
        plc_system = self.get_system("PLC")

        while True:
            if not self._is_running:
                break

            lle_response = await lle_system.poll_step()
            plc_response = await plc_system.poll_step()

            if lle_response is not None:
                logging.debug("LLE response: %s", lle_response)
                await plc_system.send_results(lle_response)

            if plc_response is not None:
                logging.debug("PLC response: %s", plc_response)
