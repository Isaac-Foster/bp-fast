from config import config, logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.infra.database.model import init_db
from src.interfaces.routers import configure_routers

app = FastAPI(
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
    import asyncio
    # nota reescrever tudo com composer e dockerfile para deploy coolify

    # Retry para conectar ao banco (útil quando roda no Docker)
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            await init_db()
            break
        except Exception:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise


configure_routers(app)
