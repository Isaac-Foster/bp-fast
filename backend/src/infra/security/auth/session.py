from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Request

from src.infra.database.connect.sql import get_session
from src.infra.database.connect.redis import session_manager
from src.adapter.repository.user import UserRepository, UserModel


@dataclass
class SessionData:
    user: UserModel
    payload: dict


async def get_current_user_cookie(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    token = request.cookies.get('session')

    if not token:
        raise HTTPException(
            status_code=401, detail='Could not validate credentials'
        )

    repository = UserRepository(session)

    data = await session_manager.get_session_data(token)

    if not data:
        raise HTTPException(
            status_code=401, detail='Could not validate credentials'
        )

    user = await repository.get(_id=data['uid'])

    return user, data
