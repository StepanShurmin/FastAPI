from datetime import date

from fastapi import APIRouter, Depends

# from pydantic.v1 import parse_obj_as
from pydantic import parse_obj_as
from fastapi_versioning import version
from fastapi import BackgroundTasks

from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBookingsInfo, SNewBooking
from app.exceptions import RoomCannotBeBookedException
from app.tasks.tasks import send_booking_confirmation_email
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("")
@version(1)
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBookingsInfo]:
    return await BookingDAO.find_all_with_images(user_id=user.id)


@router.post("", status_code=201)
@version(1)
async def add_booking(
    booking: SNewBooking,
    background_tasks: BackgroundTasks,
    user: Users = Depends(get_current_user),
):
    booking = await BookingDAO.add(
        user.id,
        booking.room_id,
        booking.date_from,
        booking.date_to,
    )
    if not booking:
        raise RoomCannotBeBookedException
    booking = parse_obj_as(SNewBooking, booking).dict()
    # send_booking_confirmation_email.delay(booking, user.email)
    # background_tasks.add_task(send_booking_confirmation_email, booking, user.email)
    return booking


@router.delete("/{booking_id}")
@version(1)
async def remove_booking(
    booking_id: int,
    current_user: Users = Depends(get_current_user),
):
    await BookingDAO.delete(id=booking_id, user_id=current_user.id)
