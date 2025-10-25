from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.connect.sql import get_session
from src.infra.connect.redis import redis_manager
from src.adapter.repository.user import UserRepository


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

    _id = await redis_manager.get_session_data(token)

    if not _id:
        raise HTTPException(
            status_code=401, detail='Could not validate credentials'
        )
    user = await repository.get(_id)

    return user
