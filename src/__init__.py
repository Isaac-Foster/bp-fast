from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.interfaces.routers import configure_routers
from src.infra.models import init_sql

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Startup async
@app.on_event('startup')
async def startup_event():
    await init_sql()


# Rotas
configure_routers(app)
