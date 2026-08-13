from pydantic import BaseModel, ConfigDict

from app.domain.enums import ElementType


class StructuralElementCreate(BaseModel):
    element_name: str
    element_type: ElementType
    material: str | None = None
    floor_id: int
    room_id: int | None = None
    dim_width: float | None = None
    dim_height: float | None = None
    dim_depth: float | None = None


class StructuralElementUpdate(BaseModel):
    element_name: str | None = None
    element_type: ElementType | None = None
    material: str | None = None
    dim_width: float | None = None
    dim_height: float | None = None
    dim_depth: float | None = None


class StructuralElementResponse(BaseModel):
    id: int
    element_name: str
    element_type: ElementType
    material: str | None
    floor_id: int
    room_id: int | None
    dim_width: float | None
    dim_height: float | None
    dim_depth: float | None

    model_config = ConfigDict(from_attributes=True)
