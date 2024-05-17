from datetime import date

from fastapi import APIRouter, Depends

# from pydantic.v1 import parse_obj_as
from pydantic import parse_obj_as
from fastapi_versioning import version
from fastapi import BackgroundTasks

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBookings
from app.exceptions import RoomCannotBeBookedException
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("")
@version(1)
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBookings]:
    return await BookingDAO.find_all(user_id=user.id)


@router.post("")
@version(1)
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    background_tasks: BackgroundTasks,
    user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBookedException
    booking_dict = parse_obj_as(SBookings, booking).dict()
    # send_booking_confirmation_email.delay(booking_dict, user.email)# отправка сообщения с помощью селери
    BackgroundTasks.add_task(send_booking_confirmation_email, booking_dict, user.email)
    return booking_dict


@router.delete("")
@version(1)
async def remove_booking(): ...
