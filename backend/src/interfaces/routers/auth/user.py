from fastapi import APIRouter, Query

from src.interfaces.schema.auth import SignUp, SignIn

router = APIRouter()


@router.post('/signup')
async def signup(data: SignUp):
    return data


@router.post('/signin')
async def signin(
    data: SignIn, totp: str = Query(default=None, pattern=r'^\d{6}$')
):
    print(totp)
    return data
