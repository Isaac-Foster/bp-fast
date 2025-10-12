from typing import Protocol

from fastapi import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.ports.repository import RepositoryPort


class ControllerPort(Protocol):
    def __init__(self, session: AsyncSession, response: Response):
        self.session = session
        self.repository: RepositoryPort = None
        self.schema: type[BaseModel] = None
