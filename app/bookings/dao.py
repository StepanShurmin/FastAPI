from datetime import date

from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Rooms
from app.logger import logger


class BookingDAO(BaseDAO):
    model = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        with booked_rooms as (
            select * from bookings
            where room_id = 1 and
            (date_from >= '2033-05-15' and date_from <= '2033-06-20') or
            (date_from <= '2033-05-15' and date_to > '2033-05-15')

        )

        select rooms.quantity - count(booked_rooms.room_id) from rooms
                left join booked_rooms on booked_rooms.room_id = rooms.id
                where rooms.id =1
                group by rooms.quantity, booked_rooms.room_id;

        """
        try:
            async with async_session_maker() as session:
                get_rooms_left = (
                    select(Rooms.quantity - func.count(Bookings.room_id).label("rooms_left"))
                    .select_from(Bookings)
                    .join(Rooms, Rooms.id == Bookings.room_id, full=True)
                    .where(
                        and_(
                            Rooms.id == room_id,
                            or_(
                                Bookings.room_id.is_(None),
                                and_(
                                    Bookings.date_from > date_from,
                                    Bookings.date_from < date_to,
                                ),
                                and_(
                                    Bookings.date_from > date_from,
                                    Bookings.date_from < date_to,
                                ),
                            ),
                        )
                    )
                    .group_by(Rooms.id, Rooms.quantity)
                )

                rooms_left = await session.execute(get_rooms_left)
                rooms_left = rooms_left.scalar()

                if not rooms_left or rooms_left > 0:
                    # if not rooms_left or None > 0:
                    get_price = await session.execute(select(Rooms.price).filter_by(id=room_id))
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=get_price.scalar(),
                        )
                        .returning(Bookings)
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()

        # @classmethod
        # async def delete_booking(cls, booking_id, current_user):
        #     async with async_session_maker() as session:
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc:"
            elif isinstance(e, Exception):
                msg = "Unknown Exc:"
            msg += "Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)
