from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import config
from src.infra.database.model import init_db
from src.interfaces.routers import configure_routers

app = FastAPI(
    title=config.app.name,
    summary=config.app.summary,
    description=config.app.description,
    version=config.app.version,
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def startup_event():
    await init_db()


configure_routers(app)
