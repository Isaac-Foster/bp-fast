from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Query, Depends, Response

from config import logger
from src.infra.connect.sql import get_session
from src.interfaces.schema.auth import SignUp, SignIn
from src.adapter.controllers.user import UserController

router = APIRouter()


@router.post('/signup')
async def signup(
    data: SignUp,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    logger.info('signup', data=data)
    user_controller = UserController(session, response)
    response = await user_controller.create(data)
    logger.info('signup response', response=response)
    return response


@router.post('/signin')
async def signin(
    data: SignIn,
    response: Response,
    totp: str = Query(default=None, pattern=r'^\d{6}$'),
    session: AsyncSession = Depends(get_session),
):
    logger.info(f'signin {data} {totp}')
    user_controller = UserController(session, response)

    response = await user_controller.signin(data, totp)
    logger.info(f'signin response {response}')
    return response
