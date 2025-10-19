from fastapi import Response

from src.core.ports.controllers import ControllerPort
from src.adapters.repository.user import UserRepository
from src.interfaces.schema.auth import UserSchema
from sqlalchemy.ext.asyncio import AsyncSession


class UserController(ControllerPort):
    def __init__(self, session: AsyncSession, response: Response):
        super().__init__(session, response)
        self.repository = UserRepository(session)
        self.schema = UserSchema
        self.response = response
