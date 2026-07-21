from pydantic import BaseModel, ConfigDict


class BuildingCreate(BaseModel):
    name: str
    address: str | None = None


class BuildingUpdate(BaseModel):
    name: str | None = None
    address: str | None = None


class BuildingResponse(BaseModel):
    id: int
    name: str
    address: str | None

    model_config = ConfigDict(from_attributes=True)
