from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils import get_uuid
from config import config, logger

from src.interfaces.schema.auth import SignUp
from src.infra.security.otp import otp_manager
from src.infra.security.auth.jwt import jwt_manager
from src.core.ports.controllers import ControllerPort
from src.adapter.repository.user import UserRepository
from src.infra.security.hashpass import hash_pass_manager
from src.infra.connect.redis import session_manager, redis_manager


async def create_auth(data, response: Response, sm):
    """Função para criar uma autenticação"""
    if config.app.auth_method == 'JWT':
        exp = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
            seconds=config.jwt.ttl
        )
        payload = dict(
            id=data.id,
            username=data.username,
            email=data.email,
            exp=exp,
        )

        if config.app.login_mode == 'UNIQUE':
            session_id = get_uuid()
            payload['session_id'] = session_id
            await sm.previous_session(session_id, data.id, config.jwt.ttl)

        return await jwt_manager.create(payload)
    else:
        session_id = get_uuid()

        data = {
            'uid': data.id,
            'session_id': session_id,
            'ttl': config.jwt.ttl,
        }

        if config.app.login_mode == 'UNIQUE':
            await sm.previous_session(session_id, data, config.jwt.ttl)

        else:
            await sm.create(session_id, data.id, config.jwt.ttl)

        response.set_cookie(
            key='session',
            value=session_id,
            max_age=config.jwt.ttl,
            httponly=True,
            secure=True,
            samesite='Strict',
        )
        return response

    return token


class UserController(ControllerPort):
    def __init__(self, session: AsyncSession, response: Response):
        super().__init__(session, response)
        self.repository = UserRepository(session)
        self.schema = SignUp
        self.response = response
        self.otp_manager = otp_manager
        self.redis_manager = redis_manager
        self.pass_manager = hash_pass_manager
        self.session_manager = session_manager

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
