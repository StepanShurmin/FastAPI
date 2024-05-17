from datetime import date

from sqlalchemy import and_, func, or_, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.models import Hotels, Rooms


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def search_for_hotels(cls, location: str, date_from: date, date_to: date):
        async with async_session_maker() as session:
            bookings_for_selected_dates = (
                select(Bookings)
                .filter(
                    or_(
                        and_(Bookings.date_from < date_from, Bookings.date_to < date_from),
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from >= date_to,
                        ),
                    )
                )
                .subquery("filtered_bookings")
            )

            hotels_rooms_left = (
                select(
                    (Hotels.rooms_quantity - func.count(bookings_for_selected_dates.c.room_id)).label("rooms_left"),
                    Rooms.hotel_id,
                )
                .select_from(Hotels)
                .outerjoin(Rooms, Rooms.hotel_id == Hotels.id)
                .outerjoin(
                    bookings_for_selected_dates,
                    bookings_for_selected_dates.c.room_id == Rooms.id,
                )
                .where(
                    Hotels.location.contains(location.title()),
                )
                .group_by(Hotels.rooms_quantity, Rooms.hotel_id)
                .cte("hotels_rooms_left")
            )

        get_hotels_info = (
            select(
                Hotels.__table__.columns,
                hotels_rooms_left.c.rooms_left,
            )
            .select_from(Hotels)
            .join(hotels_rooms_left, hotels_rooms_left.c.hotel_id == Hotels.id)
            .where(hotels_rooms_left.c.rooms_left > 0)
        )
        hotels_info = await session.execute(get_hotels_info)
        return hotels_info.all()

    @classmethod
    async def search_for_rooms(cls, hotel_id: int, date_from: date, date_to: date):
        async with async_session_maker() as session:
            bookings_for_selected_dates = (
                select(Bookings)
                .filter(
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from < date_to,
                        ),
                    )
                )
                .subquery("filtered_bookings")
            )
            rooms_left = (
                select(
                    (Rooms.quantity - func.count(bookings_for_selected_dates.c.room_id)).label("rooms_left"),
                    Rooms.id.label("room_id"),
                )
                .select_from(Rooms)
                .outerjoin(
                    bookings_for_selected_dates,
                    bookings_for_selected_dates.c.room_id == Rooms.id,
                )
                .where(Rooms.hotel_id == hotel_id)
                .group_by(Rooms.quantity, bookings_for_selected_dates.c.room_id, Rooms.id)
                .cte("rooms_left")
            )
        get_rooms_info = (
            select(
                Rooms.__table__.columns,
                rooms_left.c.rooms_left,
            )
            .select_from(Rooms)
            .join(rooms_left, rooms_left.c.room_id == Rooms.id)
            .where(rooms_left.c.rooms_left > 0)
        )
        rooms_info = await session.execute(get_rooms_info)
        return rooms_info.all()
