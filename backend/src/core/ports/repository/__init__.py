from typing import Protocol

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


class RepositoryPort(Protocol):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = None
        self.schema: type[BaseModel] = None
