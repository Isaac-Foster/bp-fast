from fastapi import APIRouter, Request

from config import settings

router = APIRouter()


@router.get('/info_me')
async def info(request: Request):
    ip = request.client.host
    user_agent = request.headers.get('user-agent')
    return {'ip': ip, 'user_agent': user_agent}


@router.get('/configs')
async def info_me():
    return settings.model_dump(by_alias=False)
