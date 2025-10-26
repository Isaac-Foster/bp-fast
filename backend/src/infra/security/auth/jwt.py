from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from src.infra.connect.sql import get_session
from src.infra.connect.redis import session_manager

from src.adapter.repository.user import UserRepository


@dataclass
class AuthResponse:
    user: dict
    payload: dict


@dataclass
class Authorization:
    access_token: str
    token_type: str = 'Bearer'
    expires_at: float = 0


class JWTManager:
    def __init__(self):
        pass

    def create(self, data: dict) -> Authorization:
        token = jwt.encode(
            data, config.jwt.secret, algorithm=config.jwt.algorithm
        )
        return Authorization(access_token=token, expires_at=data['exp'])

    def validate(self, token: str) -> dict:
        data = jwt.decode(
            token, config.jwt.secret, algorithms=[config.jwt.algorithm]
        )
        return data

    def decode_ignore_exp(self, token: str) -> dict:
        data = jwt.decode(
            token,
            config.jwt.secret,
            algorithms=[config.jwt.algorithm],
            options={'verify_exp': False},
        )
        return data


jwt_manager = JWTManager()


async def get_current_user_jwt(
    bearer: str = Depends(HTTPBearer()),
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    repository = UserRepository(session)

    if not bearer or not bearer.credentials:
        raise HTTPException(status_code=401, detail='Unauthorized')

    token = bearer.credentials

    try:
        payload = jwt_manager.validate(token)

        if config.app.login_mode == 'UNIQUE':
            is_already = await session_manager.get_session_data(
                session_id=payload['session_id']
            )
            if not is_already:
                raise HTTPException(status_code=401, detail='Unauthorized')

    except jwt.exceptions.ExpiredSignatureError:
        payload = jwt_manager.decode_ignore_exp(token)
        user = await repository.get(payload['id'])
        user.allowed = False
        await repository.session.commit()
        await repository.session.refresh(user)
        if config.app.login_mode == 'UNIQUE':
            await session_manager.delete_session(
                session_id=payload['session_id']
            )
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    user = await repository.get(payload['id'])
    return AuthResponse(user=user, payload=payload)


if __name__ == '__main__':
    jwt_manager = JWTManager()
    token = jwt_manager.create({'user_id': 1})
    print(token)
    print(jwt_manager.validate(token))
