from config import logger
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapter.controller.user import UserController
from src.infra.database.connect.sql import get_session
from src.interfaces.schema.auth import SignIn, SignUp

router = APIRouter()


@router.post('/signup')
async def signup(
    data: SignUp,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
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
    logger.info(f'signin {totp}')
    user_controller = UserController(session, response)

    response = await user_controller.signin(data, totp)
    return response
