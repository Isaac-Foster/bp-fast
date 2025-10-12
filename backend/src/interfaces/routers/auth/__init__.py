from fastapi import APIRouter


def configure_router(router_root):
    from .user import router as user_router

    router = APIRouter()
    router.include_router(user_router)
    router_root.include_router(router)
    return router_root
