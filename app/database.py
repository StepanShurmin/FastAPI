from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

if settings.MODE == "TEST":
    DATABASE_URL = settings.T_DATABASE_URL
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {}

# assert settings.MODE == "TEST"

engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
