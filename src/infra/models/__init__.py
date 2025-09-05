from src.infra.connection.sql import engine, register


async def init_sql():
    # importa os modelos para registrar os mapeamentos
    from . import (
        user,  # noqa
    )

    async with engine.begin() as conn:
        await conn.run_sync(register.metadata.create_all)
