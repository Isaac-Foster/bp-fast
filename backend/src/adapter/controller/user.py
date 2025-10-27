import io
import base64
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

from fastapi import HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse, JSONResponse


from src.utils import get_uuid
from src.utils.helpers.sql import save_and_refresh
from config import config, logger

from src.interfaces.schema.auth import SignUp
from src.infra.security.otp import otp_manager
from src.infra.security.auth.jwt import jwt_manager
from src.core.ports.controllers import ControllerPort
from src.adapter.repository.user import UserRepository
from src.infra.security.hashpass import hash_pass_manager
from src.infra.connect.redis import session_manager, redis_manager
from src.core.services.user_business_rules import UserBusinessRules


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
            await sm.previous_session(session_id, payload, config.redis.ttl)
        return jwt_manager.create(payload)
    else:
        session_id = get_uuid()

        data = dict(
            id=data.id,
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

    # ====== Métodos Auxiliares ======

    async def _validate_user_exists(self, user: SignUp):
        """Valida se usuário existe no banco"""
        already_exists = await self.repository.find(user)
        if not already_exists:
            raise HTTPException(status_code=404, detail='User not found')
        return already_exists[0]

    async def _check_user_blocked(self, user_model):
        """Verifica se usuário está bloqueado"""
        if user_model.blocked:
            raise HTTPException(status_code=401, detail='User blocked')

    async def _check_attempts_and_block(self, user_model):
        """Verifica tentativas e bloqueia se necessário"""
        if UserBusinessRules.should_block_user(user_model.attempts):
            user_model.blocked = True
            await save_and_refresh(self.session, user_model)
            raise HTTPException(status_code=401, detail='User blocked')

    async def _validate_password(self, user: SignUp, user_model):
        """Valida senha e incrementa tentativas se inválida"""
        if not self.pass_manager.verify(user.password, user_model.password):
            user_model.attempts += 1
            await save_and_refresh(self.session, user_model)
            raise HTTPException(
                status_code=401, detail='Invalid user or password'
            )

    async def _setup_initial_otp(self, user_model):
        """Configura OTP inicial para usuário sem secret"""
        logger.info(f'User {user_model.id} has no secret_otp')
        secret_otp = self.otp_manager.generate_secret()
        user_model.secret_otp = secret_otp
        await save_and_refresh(self.session, user_model)
        return True

    async def _generate_otp_qr_response(
        self, user_model
    ) -> dict | StreamingResponse:
        """Gera resposta com QR code do OTP"""
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

        return StreamingResponse(
            io.BytesIO(_image),
            media_type='image/png',
            headers={
                'Cache-Control': 'no-store',
                'Content-Disposition': 'inline; filename="otp.png"',
            },
        )

    async def _verify_otp_code(self, user_model, totp: str):
        """Verifica código OTP"""
        if not self.otp_manager.verify_code(user_model.secret_otp, totp):
            user_model.attempts += 1
            await save_and_refresh(self.session, user_model)
            raise HTTPException(status_code=401, detail='Invalid OTP')

        if not user_model.otp:
            user_model.otp = True

    async def _finalize_login(self, user_model):
        """Finaliza login resetando tentativas e habilitando usuário"""
        user_model.allowed = True
        user_model.attempts = 0
        await save_and_refresh(self.session, user_model)

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
        """Fluxo de autenticação com validação e OTP"""
        # 1. Validar usuário existe
        user_model = await self._validate_user_exists(user)

        # 2. Verificar bloqueio
        await self._check_user_blocked(user_model)
        await self._check_attempts_and_block(user_model)

        # 3. Validar senha
        await self._validate_password(user, user_model)

        # 4. Setup OTP inicial se necessário
        if not user_model.secret_otp:
            await self._setup_initial_otp(user_model)
            return await self._generate_otp_qr_response(user_model)

        # 5. Verificar se precisa validar OTP
        if not user_model.otp and totp is None:
            raise HTTPException(status_code=401, detail='OTP not enabled')

        # 6. Validar código OTP
        if totp:
            await self._verify_otp_code(user_model, totp)

        # 7. Finalizar login
        await self._finalize_login(user_model)

        # 8. Criar autenticação
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
