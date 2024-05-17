from datetime import date
from typing import Optional

from pydantic import BaseModel


class SBookings(BaseModel):
    id: int
    room_id: int
    user_id: int
    date_from: date
    date_to: date
    price: int
    total_cost: int
    total_days: int

    class Config:
        from_attributes = True


class SBookingsInfo(BaseModel):
    hotel_name: str
    room_name: str
    room_description: Optional[str]
    room_services: list[str]
    date_from: date
    date_to: date

    class Config:
        from_attributes = True
