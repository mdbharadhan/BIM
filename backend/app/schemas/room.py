from pydantic import BaseModel, ConfigDict


class RoomCreate(BaseModel):
    room_name: str
    room_number: str | None = None
    room_type: str | None = None
    floor_id: int
    area: float | None = None
    occupancy: int | None = None


class RoomUpdate(BaseModel):
    room_name: str | None = None
    room_number: str | None = None
    room_type: str | None = None
    area: float | None = None
    occupancy: int | None = None


class RoomResponse(BaseModel):
    id: int
    room_name: str
    room_number: str | None
    room_type: str | None
    floor_id: int
    area: float | None
    occupancy: int | None

    model_config = ConfigDict(from_attributes=True)
