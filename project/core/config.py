import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    VERSION: str
    ENVIRONMENT: str
    BASE_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_HOUR: int = 3600
    ACCESS_TOKEN_EXPIRE_24HOURS: int = 24
    ACCESS_TOKEN_EXPIRE_7DAYS: int = 7
    ACCESS_TOKEN_EXPIRE_WEEK: int = 1

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_URL: str | None = None

    DATABASE_URL: str
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 5
    POOL_TIMEOUT: int = 20
    CONNECT_TIMEOUT: int = 10
    COMMAND_TIMEOUT: int = 60

    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USE_TLS: bool
    MAIL_USERNAME: str
    MAIL_PASSWORD: str

    class Config:
        if os.getenv("ENVIRONMENT", "development") != "production":
            env_file = os.path.expanduser("~/Desktop/auth_system_open_source/.env")
            env_file_encoding = "utf-8"


settings = Settings()
