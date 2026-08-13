from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import ChecklistInstanceStatus
from app.schemas.checklist_instance_item import ChecklistInstanceItemResponse
from app.schemas.mixins import EntityRef


class ChecklistInstanceCreate(EntityRef):
    template_id: int


class ChecklistInstanceResponse(BaseModel):
    id: int
    entity_type: str | None
    entity_id: int | None
    template_id: int | None
    status: ChecklistInstanceStatus
    created_at: datetime
    items: list[ChecklistInstanceItemResponse]

    model_config = ConfigDict(from_attributes=True)
