from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

import jwt
from pydantic import BaseModel
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from src.infra.connect.sql import get_session

# from src.infra.security.hashpass import hash_pass_manager
from src.adapter.repository.user import UserRepository


class AuthResponse(BaseModel):
    user: BaseModel
    payload: dict


class Authorization(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    expires_at: float = 0


class JWTManager:
    def __init__(self):
        pass

    def create(self, data: dict) -> Authorization:
        to_encode = data.copy()

        to_encode.update(
            {
                'exp': datetime.now(tz=ZoneInfo('UTC'))
                + timedelta(minutes=config.jwt.expiration_time).timestamp()
            }
        )

        token = jwt.encode(
            to_encode, config.jwt.secret, algorithm=config.jwt.algorithm
        )
        return Authorization(access_token=token, expires_at=to_encode['exp'])

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


async def get_current_user_jwt(
    bearer: str = Depends(HTTPBearer()),
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    repository = UserRepository(session)

    if not bearer or not bearer.credentials:
        raise HTTPException(status_code=401, detail='Unauthorized')

    token = bearer.credentials

    try:
        payload = JWTManager().validate(token)
    except jwt.exceptions.ExpiredSignatureError:
        payload = JWTManager().decode_ignore_exp(token)
        user = await repository.get(payload['id'])
        user.allowed = False
        await repository.session.commit()
        await repository.session.refresh(user)
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
