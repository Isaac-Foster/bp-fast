from fastapi import APIRouter

from config import logger

router = APIRouter(prefix='/api')


def configure_routers(app):
    from .test import init_test_router

    init_test_router(app)
    logger.success('end call configure_routers')
