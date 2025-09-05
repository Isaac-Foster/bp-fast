from fastapi import APIRouter

from config import logger

router = APIRouter(
    prefix='/test',
    tags=['Test'],
)


def init_test_router(app):
    from . import ping, info_me

    router.include_router(ping.router)
    router.include_router(info_me.router)
    app.include_router(router)
    logger.success('Test router initialized')
