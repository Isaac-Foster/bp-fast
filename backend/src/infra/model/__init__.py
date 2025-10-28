from . import (
    user,  # noqa
    fingerprint,  # noqa
    config,  # noqa
)

from src.infra.connect.sql import register, engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(register.metadata.create_all)
