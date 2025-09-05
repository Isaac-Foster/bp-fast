from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LoadEnvFile(BaseSettings):
    model_config = {
        'env_file': '.env',
        'extra': 'allow',
    }

class DatabaseSql(BaseModel):
    drivername: str
    host: str = Field(default='localhost', alias='db_host')
    port: int = Field(alias='db_port')
    user: str = Field(alias='db_user')
    password: str = Field(default='', alias='db_password')
    database: str = Field(alias='db_name')


class Redis(BaseModel):
    host: str = Field(default='localhost', alias='redis_host')
    port: int = Field(default=6379, alias='redis_port')


class Jwt(BaseModel):
    secret_key: str = Field(alias='secret_key_jwt')
    algorithm: str = Field(alias='algorithm_jwt')
    expiration_time: int = Field(alias='expiration_time_jwt')


class Settings(BaseModel):
    root_path: Path = Path(__file__).parent.parent
    database: DatabaseSql = None
    redis: Redis = None
    jwt: Jwt = None

    def model_post_init(self, __context):
        load_env_file = LoadEnvFile()
        self.database = DatabaseSql(**load_env_file.dict())
        self.redis = Redis(**load_env_file.dict())
        self.jwt = Jwt(**load_env_file.dict())

# singleton -> config
settings = Settings()

logger.add(
    'logs/app.log',
    # level='WARNING', # -> trigger event LEVEL for register.
    rotation='2 MB',
    compression='zip',
    retention='1 week',
    format='{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message} | {file} | {function} | {line}',
)
