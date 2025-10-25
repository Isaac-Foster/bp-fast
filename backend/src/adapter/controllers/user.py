from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.interfaces.schema.auth import SignUp
from src.core.ports.controllers import ControllerPort
from src.adapter.repository.user import UserRepository
from src.infra.security.hashpass import hash_pass_manager


class UserController(ControllerPort):
    def __init__(self, session: AsyncSession, response: Response):
        super().__init__(session, response)
        self.repository = UserRepository(session)
        self.schema = SignUp
        self.response = response
        self.pass_manager = hash_pass_manager

    async def create(self, user: SignUp):
        already_exists = await self.repository.find(user)

        if already_exists:
            raise HTTPException(status_code=400, detail='User already exists')

        user.password = self.pass_manager.hash(user.password)
        user = await self.repository.create(user)
        return user

    async def get(self, _id):
        return await self.repository.get(_id)
