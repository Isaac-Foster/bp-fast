from typing import Protocol

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


class RepositoryPort(Protocol):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = None
        self.schema: type[BaseModel] = None

    async def create(self, data: BaseModel):
        pass

    async def get(self, id):
        pass

    async def get_all(self):
        pass

    async def update(self, id, data: BaseModel):
        pass

    async def delete(self, id):
        pass

    async def search(self, **kwargs):
        pass

    async def find(self, **kwargs):
        pass
