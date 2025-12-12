from src.infra.database.connect.sql import engine, register

from . import (
    config,  # noqa
    fingerprint,  # noqa
    user,  # noqa
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(register.metadata.create_all)
