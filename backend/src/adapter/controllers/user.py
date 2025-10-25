from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.interfaces.schema.auth import SignUp
from src.core.ports.controllers import ControllerPort
from src.adapter.repository.user import UserRepository
from src.infra.security.hashpass import hash_pass_manager
from src.infra.security.otp import otp_manager


class UserController(ControllerPort):
    def __init__(self, session: AsyncSession, response: Response):
        super().__init__(session, response)
        self.repository = UserRepository(session)
        self.schema = SignUp
        self.response = response
        self.pass_manager = hash_pass_manager
        self.otp_manager = otp_manager

    async def create(self, user: SignUp):
        already_exists = await self.repository.find(user)

        if already_exists:
            logger.debug(f'User already exists {user}')
            raise HTTPException(status_code=400, detail='User already exists')

        user.password = self.pass_manager.hash(user.password)
        user = await self.repository.create(user)
        logger.success(f'User created {user}')
        return user

    async def signin(self, user: SignUp, totp: str = None):
        pass

    async def get(self, _id):
        return await self.repository.get(_id)

    async def generate_otp(self, _id: int):
        model = await self.repository.get(_id)

        if not model:
            raise HTTPException(status_code=404, detail='User not found')

        self.otp_manager.generate_current_otp(model.otp_secret)
