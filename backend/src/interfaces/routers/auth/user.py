from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.interfaces.schema.auth import Signup

router = APIRouter()


@router.post('/signup')
async def signup(data: Signup):
    return data


@router.post('/signin')
async def signin(data: OAuth2PasswordRequestForm = Depends()):
    return data
