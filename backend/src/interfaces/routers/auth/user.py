from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Query, Depends, Response

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
    user_controller = UserController(session, response)
    response = await user_controller.create(data)
    return response


@router.post('/signin')
async def signin(
    data: SignIn,
    response: Response,
    totp: str = Query(default=None, pattern=r'^\d{6}$'),
    session: AsyncSession = Depends(get_session),
):
    user_controller = UserController(session, response)
    return await user_controller.signin(data, totp)


@router.get('/token')
async def token(token: str = Depends(HTTPBearer())):
    return {'token': token.credentials}
