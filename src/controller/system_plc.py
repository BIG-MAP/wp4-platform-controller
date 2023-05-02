from dataclasses import dataclass
from typing import Any

from asyncua import Client as UAClient
from asyncua import ua
from controller.system import SystemInterface


@dataclass
class PLCClientSettings:
    namespace_id: int
    lle_id: int
    lle_is_started_id: int
    lle_status_id: int
    lle_results_id: int


class Client:
    def __init__(self, url: str, settings: PLCClientSettings):
        self.url = url
        self.settings = settings

    async def get_is_started(self) -> bool:
        path = self.node_id_for_id(self.settings.lle_is_started_id)

        async with UAClient(self.url) as client:
            node = client.get_node(path)
            return await node.read_value()

    async def set_is_started(self, value: bool) -> Any:
        path = self.node_id_for_id(self.settings.lle_is_started_id)

        async with UAClient(self.url) as client:
            node = client.get_node(path)
            return await node.write_value(value)

    async def set_lle_status(self, status: str) -> Any:
        path = self.node_id_for_id(self.settings.lle_status_id)

        async with UAClient(self.url) as client:
            node = client.get_node(path)
            return await node.write_value(status)

    async def set_lle_results(self, results: Any) -> Any:
        path = self.node_id_for_id(self.settings.lle_results_id)

        async with UAClient(self.url) as client:
            node = client.get_node(path)
            return await node.write_value(results)

    @staticmethod
    def path_from_ns_and_id(ns: int, id: int) -> str:
        return f"ns={ns};i={id}"

    def node_id_for_id(self, id: int) -> ua.NodeId:
        return ua.NodeId(id, self.settings.namespace_id)


class PLCSystem(SystemInterface):
    """
    PLCSystem is a class responsible from interacting with the PLC system. It waits for a start signal from the PLC,
    then it launches downstream systems and starts polling for their status.
    """

    def __init__(
        self,
        name: str,
        url: str,
        version: str = "0.0.0",
        client_settings: PLCClientSettings | None = None,
    ):
        super().__init__(name, url, version)
        self._client = Client(url, client_settings)
        self._is_running = False

    async def should_start(self) -> bool:
        return await self._client.get_is_started()

    async def set_is_started(self, value: bool) -> Any:
        return await self._client.set_is_started(value)

    async def set_lle_status(self, status: str) -> Any:
        return await self._client.set_lle_status(status)

    async def set_lle_results(self, results: Any) -> Any:
        return await self._client.set_lle_results(results)
