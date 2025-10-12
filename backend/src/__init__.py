from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.interfaces.routers import configure_routers
from src.infra.model import init_db

app = FastAPI()

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
