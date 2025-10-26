import io
import base64
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse, JSONResponse


from src.utils import get_uuid
from config import config, logger

from src.interfaces.schema.auth import SignUp
from src.infra.security.otp import otp_manager
from src.infra.security.auth.jwt import jwt_manager
from src.core.ports.controllers import ControllerPort
from src.adapter.repository.user import UserRepository
from src.infra.security.hashpass import hash_pass_manager
from src.infra.connect.redis import session_manager, redis_manager


def _ensure_png_bytes(image_any) -> bytes:
    if isinstance(image_any, bytes):
        return image_any
    if isinstance(image_any, str):
        # assume base64 sem prefixo data:; se tiver, remova o cabeçalho antes
        return base64.b64decode(image_any)
    try:
        # Tentativa: objeto PIL.Image
        from PIL import Image

        if isinstance(image_any, Image.Image):
            buf = io.BytesIO()
            image_any.save(buf, format='PNG')
            return buf.getvalue()
    except Exception:
        pass
    raise TypeError('Formato de imagem não suportado')


async def create_auth(data, response: Response, sm: session_manager):
    """Função para criar uma autenticação"""
    if config.app.auth_method == 'JWT':
        exp = (
            datetime.now(tz=ZoneInfo('UTC'))
            + timedelta(seconds=config.jwt.expiration_time)
        ).timestamp()

        payload = dict(
            id=data.id,
            username=data.username,
            email=data.email,
            exp=exp,
        )

        if config.app.login_mode == 'UNIQUE':
            session_id = get_uuid()
            payload['session_id'] = session_id
            payload['uid'] = data.id
            await sm.previous_session(session_id, payload, config.redis.ttl)
        return jwt_manager.create(payload)
    else:
        session_id = get_uuid()

        data = dict(
            uid=data.id,
            session_id=session_id,
            ttl=config.redis.ttl,
        )

        if config.app.login_mode == 'UNIQUE':
            await sm.previous_session(session_id, data, config.redis.ttl)

        else:
            await sm.create(session_id, data.id, config.redis.ttl)

        response.set_cookie(
            key='session',
            value=session_id,
            max_age=config.redis.ttl,
            httponly=True,
            secure=True,
            samesite='Strict',
        )
        # message temporary
        return {'message': 'login successfully'}

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
        already_exists = await self.repository.find(user)

        if not already_exists:
            raise HTTPException(status_code=404, detail='User not found')

        user_model = already_exists[0]

        if user_model.blocked:
            raise HTTPException(status_code=401, detail='User blocked')

        if user_model.attempts >= 3:
            user_model.blocked = True
            await self.session.commit()
            await self.session.refresh(user_model)
            raise HTTPException(status_code=401, detail='User blocked')

        if not self.pass_manager.verify(user.password, user_model.password):
            user_model.attempts += 1
            await self.session.commit()
            await self.session.refresh(user_model)
            raise HTTPException(
                status_code=401, detail='Invalid user or password'
            )

        create_now = False

        if not user_model.secret_otp:
            create_now = True
            logger.info(f'User {user_model} has no secret_otp')
            secret_otp = self.otp_manager.generate_secret()
            user_model.secret_otp = secret_otp

            await self.session.commit()
            await self.session.refresh(user_model)
        else:
            if not user_model.otp and not totp and not create_now:
                raise HTTPException(status_code=401, detail='OTP not enabled')

            elif not user_model.otp and not totp and create_now:
                image = self.otp_manager.generate_qr_code(
                    secret=user_model.secret_otp,
                    name=user_model.username,
                    app_name='MyApp',
                )
                _image = _ensure_png_bytes(image)
                self.response.status_code = 201

                if config.app.env == 'PROD':
                    return JSONResponse(
                        status_code=201,
                        content={
                            'secret': user_model.secret_otp,
                            'image': _image,
                        },
                    )

                if config.app.env == 'DEV':
                    return StreamingResponse(
                        io.BytesIO(_image),
                        media_type='image/png',
                        headers={
                            'Cache-Control': 'no-store',  # evite cache se preferir
                            'Content-Disposition': 'inline; filename="otp.png"',
                        },
                    )
            if totp is None:
                raise HTTPException(status_code=401, detail='totp is required')

            if totp:
                if not self.otp_manager.verify_code(
                    user_model.secret_otp, totp
                ):
                    user_model.attempts += 1
                    await self.session.commit()
                    await self.session.refresh(user_model)
                    raise HTTPException(status_code=401, detail='Invalid OTP')

                if not user_model.otp:
                    user_model.otp = True

                user_model.allowed = True
                user_model.attempts = 0
                await self.session.commit()
                await self.session.refresh(user_model)
                return await create_auth(
                    user_model, self.response, self.session_manager
                )

    async def get(self, _id):
        return await self.repository.get(_id)

    async def generate_otp(self, _id: int):
        model = await self.repository.get(_id)

        if not model:
            raise HTTPException(status_code=404, detail='User not found')

        self.otp_manager.generate_current_otp(model.otp_secret)
