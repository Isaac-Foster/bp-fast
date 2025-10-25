from config import config, logger
from .session import get_current_user_cookie
from .jwt import get_current_user_jwt


def get_current_user():
    if config.app.auth_method == 'JWT':
        logger.debug('Using JWT for authentication')
        return get_current_user_jwt
    logger.debug('Using cookie for authentication')
    return get_current_user_cookie
