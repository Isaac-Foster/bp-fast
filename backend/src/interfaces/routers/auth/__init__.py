from config import config, logger
from fastapi import APIRouter, Depends
from src.infra.security.auth import (
    get_current_user_cookie,
    get_current_user_jwt,
)


def configure_router(router_root):
    from .auth import router as auth_router
    from .user import router as user_router

    logger.info('include auth router')
    logger.debug('Auth method selected: %s' % config.app.auth_method)

    router = APIRouter(
        prefix='/auth',
        tags=['auth'],
    )
    router.include_router(user_router)

    router.include_router(
        auth_router,
        dependencies=[
            Depends(get_current_user_jwt)
            if config.app.auth_method == 'JWT'
            else Depends(get_current_user_cookie)
        ],
    )
    router_root.include_router(router)
    return router_root
