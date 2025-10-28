from fastapi import APIRouter, FastAPI


def configure_routers(app: FastAPI):
    from .auth import configure_router as auth_router

    router = APIRouter(
        prefix='/api',
    )
    auth_router(router)
    app.include_router(router)
