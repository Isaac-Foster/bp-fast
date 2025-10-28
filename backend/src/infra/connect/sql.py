# db.py
from typing import AsyncIterator

from sqlalchemy.engine import URL

from sqlalchemy.orm import registry
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from config import config


URI = URL.create(
    drivername=config.postgres.drivername,
    username=config.postgres.user,
    password=config.postgres.password,
    host=config.postgres.host,
    port=config.postgres.port,
    database=config.postgres.database,
    # query={'charset': config.postgres.charset},
)


# ---- ENGINE & SESSION ---------------------------------------
engine = create_async_engine(
    url=URI,
    echo=False,  # mude para True para ver SQL no console
    pool_pre_ping=True,  # evita conexões mortas
    pool_recycle=1800,  # reaproveita conexões a cada 30min
    future=True,
)

Session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


register = registry()


# ---- Session helper (útil p/ FastAPI ou scripts) ------------
async def get_session() -> AsyncIterator[AsyncSession]:
    async with Session() as session:
        yield session
