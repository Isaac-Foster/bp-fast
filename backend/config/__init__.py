from loguru import logger

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LoadEnvFile(BaseSettings):
    model_config = {
        # Carrega o arquivo .env, mas variáveis de ambiente têm prioridade (comportamento padrão)
        'env_file': '.env',
        'env_file_encoding': 'utf-8',
        'extra': 'allow',
        'case_sensitive': False,
        # IMPORTANTE: O pydantic-settings por padrão prioriza variáveis de ambiente sobre o arquivo .env
    }


class Mysql(BaseModel):
    drivername: str = Field(..., alias='mysql_drivername')
    user: str = Field(..., alias='mysql_db_user')
    password: str = Field(..., alias='mysql_db_password')
    host: str = Field(..., alias='mysql_db_host')
    port: str = Field(..., alias='mysql_db_port')
    database: str = Field(..., alias='mysql_db_name')
    charset: str = Field(..., alias='mysql_charset')


class Postgres(BaseModel):
    drivername: str = Field(..., alias='postgres_drivername')
    user: str = Field(..., alias='postgres_db_user')
    password: str = Field(..., alias='postgres_db_password')
    host: str = Field(..., alias='postgres_db_host')
    port: str = Field(..., alias='postgres_db_port')
    database: str = Field(..., alias='postgres_db_name')
    charset: str = Field(..., alias='postgres_charset')


class JWT(BaseModel):
    secret: str = Field(..., alias='jwt_secret')
    algorithm: str = Field(..., alias='jwt_algorithm')
    expiration_time: int = Field(..., alias='jwt_expiration_time')

    def model_post_init(self, __contex):
        self.secret = self.secret.replace('\n', '')


class Redis(BaseModel):
    host: str = Field(..., alias='redis_host')
    port: str = Field(..., alias='redis_port')
    db: int = Field(..., alias='redis_db')
    ttl: int = Field(..., alias='redis_ttl')


class AppConfig(BaseModel):
    name: str = Field(..., alias='app_name')
    version: str = Field(..., alias='app_version')
    description: str = Field(..., alias='app_description')
    summary: str = Field(..., alias='app_summary')
    auth_method: str = Field(..., alias='app_auth_method')
    login_mode: str = Field(..., alias='app_login_mode')
    env: str = Field(..., alias='app_env')


class TOTP(BaseModel):
    interval: int = Field(..., alias='totp_interval')
    digits: int = Field(..., alias='totp_digits')
    window: int = Field(..., alias='totp_window')


class Config(BaseModel):
    # mysql: Mysql = None  # Comentado - usar postgres
    postgres: Postgres = None
    jwt: JWT = None
    redis: Redis = None
    app: AppConfig = None
    totp: TOTP = None

    def model_post_init(self, __context):
        import os

        load_env_file = LoadEnvFile()
        env_dict = load_env_file.model_dump()

        # Sobrescreve com variáveis de ambiente se estiverem definidas (prioridade)
        # Isso garante que variáveis de ambiente do Docker Compose tenham prioridade
        if os.getenv('POSTGRES_DB_HOST'):
            env_dict['postgres_db_host'] = os.getenv('POSTGRES_DB_HOST')
        if os.getenv('REDIS_HOST'):
            env_dict['redis_host'] = os.getenv('REDIS_HOST')

        # self.mysql = Mysql(**env_dict)  # Comentado - usar postgres
        self.postgres = Postgres(**env_dict)
        self.jwt = JWT(**env_dict)
        self.redis = Redis(**env_dict)
        self.app = AppConfig(**env_dict)
        self.totp = TOTP(**env_dict)


# singleton leitura unica do .env
config = Config()


logger.add(
    'logs/app.log',
    level='WARNING',  # -> trigger event LEVEL for register.
    rotation='2 MB',
    compression='zip',
    retention='1 week',
    format='{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message} | {file} | {function} | {line}',
)


if __name__ == '__main__':
    logger.info('Config loaded')
    logger.info(f'Config: {config}')
