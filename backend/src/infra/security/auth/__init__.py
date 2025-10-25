from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from src.infra.connect.sql import get_session

# from src.infra.security.hashpass import hash_pass_manager
from src.adapter.repository.user import UserRepository


o2auth_schema = HTTPBearer()


class JWTManager:
    def __init__(self):
        pass

    def create(self, data: dict) -> str:
        to_encode = data.copy()

        to_encode.update(
            {
                'exp': datetime.now(tz=ZoneInfo('UTC'))
                + timedelta(minutes=config.jwt.expiration_time)
            }
        )

        token = jwt.encode(
            to_encode, config.jwt.secret, algorithm=config.jwt.algorithm
        )
        return token

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


async def get_current_user(
    token: str = Depends(HTTPBearer()),
    session: AsyncSession = Depends(get_session),
):
    repository = UserRepository(session)
    try:
        payload = JWTManager().validate(token.credentials)
    except jwt.exceptions.ExpiredSignatureError:
        payload = JWTManager().decode_ignore_exp(token.credentials)
        user = await repository.find_by_id(payload['id'])
        user.allowed = False
        await repository.session.commit()
        await repository.session.refresh(user)
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    user = await repository.find_by_id(payload['id'])

    return user, payload


if __name__ == '__main__':
    jwt_manager = JWTManager()
    token = jwt_manager.create({'user_id': 1})
    print(token)
    print(jwt_manager.validate(token))
