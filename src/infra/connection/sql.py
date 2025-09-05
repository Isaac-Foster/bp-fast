from sqlalchemy.orm import registry
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings

# ✅ String de conexão com driver async
URI = URL.create(
    drivername=settings.database.drivername,
    username=settings.database.user,
    password=settings.database.password,
    host=settings.database.host,
    port=settings.database.port,
    database=settings.database.database,
)
# ✅ Registry para mapeamento ORM
register = registry()

# ✅ Criação do engine assíncrono com parâmetros de pool
engine = create_async_engine(
    URI,
    pool_size=15,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False,  # Ative para logs de SQL
)

# ✅ Criando o async sessionmaker
AsyncSession = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
