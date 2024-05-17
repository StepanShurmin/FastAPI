from typing import Literal

from pydantic.v1 import BaseSettings, root_validator


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["DEBUG", "INFO"]

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @root_validator
    def get_database_url(cls, v):
        v["DATABASE_URL"] = (
            f"postgresql+asyncpg://{v['DB_USER']}:{v['DB_PASS']}@{v['DB_HOST']}:{v['DB_PORT']}/{v['DB_NAME']}"
        )
        return v

    T_DB_HOST: str
    T_DB_PORT: int
    T_DB_USER: str
    T_DB_PASS: str
    T_DB_NAME: str

    @root_validator
    def get_test_database_url(cls, v):
        v["T_DATABASE_URL"] = (
            f"postgresql+asyncpg://{v['T_DB_USER']}:{v['T_DB_PASS']}@{v['T_DB_HOST']}:{v['T_DB_PORT']}/{v['T_DB_NAME']}"
        )
        return v

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    EMAIL_USE_SSL: bool

    REDIS_HOST: str
    REDIS_PORT: int

    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env"


settings = Settings()
