from pydantic import BaseModel, ConfigDict


class FloorCreate(BaseModel):
    floor_name: str
    floor_number: int
    building_id: int


class FloorUpdate(BaseModel):
    floor_name: str | None = None
    floor_number: int | None = None


class FloorResponse(BaseModel):
    id: int
    floor_name: str
    floor_number: int
    building_id: int

    model_config = ConfigDict(from_attributes=True)
