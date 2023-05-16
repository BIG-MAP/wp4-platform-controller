import requests

from controller.lle.settings import Settings


class Client:
    def __init__(self, url: str):
        self.url = url

    async def get_status(self) -> dict:
        response = requests.get(f"{self.url}/status")
        return response.json()

    async def start_settling(self, settings: Settings) -> dict:
        response = requests.post(
            f"{self.url}/startSettling", json=settings.dict(exclude={"liquid_type"})
        )
        return response.json()

    async def start_draining(self, settings: Settings) -> dict:
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
