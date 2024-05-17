class HotelInfo:
    id: int
    name: str
    location: str
    rooms_quantity: int
    image_id: int

    class Config:
        from_attributes = True


class RoomInfo:
    id: int
    hotel_id: int
    name: str
    description: str
    price: int

    quantity: int
    image_id: int

    class Config:
        from_attributes = True
