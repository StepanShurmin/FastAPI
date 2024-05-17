from sqlalchemy import insert, select

from app.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            # return result.mappings().all() # line 155, in serialize_responseraise ResponseValidationError(fastapi.exceptions.ResponseValidationError: 16 validation errors:{'type': 'missing', 'loc': ('response', 0, 'id'), 'msg': 'Field required', 'input': {'Bookings': <app.bookings.models.Bookings object at 0x1058a6780>}, 'url': 'https://errors.pydantic.dev/2.6/v/missing'}
            return result.scalars().all()

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            result = await session.execute(query)
            result = await session.commit()
