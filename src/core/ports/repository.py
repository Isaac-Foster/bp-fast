from typing import Protocol


class RepositoryPort(Protocol):
    def __init__(self):
        pass

    async def create(self):
        pass

    async def update(self):
        pass

    async def delete(self):
        pass

    async def get(self):
        pass

    async def get_all(self):
        pass
