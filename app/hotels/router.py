import asyncio
from datetime import date, datetime

from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache

# from pydantic.v1 import parse_obj_as
from pydantic import parse_obj_as

from app.hotels.dao import HotelDAO
from app.hotels.schemas import HotelInfo, RoomInfo

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("/{location}")
@cache(expire=20)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date = Query(description=f"например {datetime.now().date()}"),
    date_to: date = Query(description=f"например {datetime.now().date()}"),
):  # -> list[HotelInfo]:
    await asyncio.sleep(3)
    hotels = await HotelDAO.search_for_hotels(location, date_from, date_to)
    hotels_json = parse_obj_as(list[HotelInfo], hotels)
    return hotels_json


@router.get("/{hotel_id}/rooms")
async def get_rooms_by_time(
    hotel_id: int,
    date_from: date = Query(description=f"например {datetime.now().date()}"),
    date_to: date = Query(description=f"например {datetime.now().date()}"),
):  # -> list[RoomInfo]:
    rooms = await HotelDAO.search_for_rooms(hotel_id, date_from, date_to)
    # rooms_json = parse_obj_as(list[RoomInfo], rooms)
    return rooms
