from pydantic import BaseModel, ConfigDict

from app.schemas.checklist_template_item import (
    ChecklistTemplateItemCreate,
    ChecklistTemplateItemResponse,
)


class ChecklistTemplateCreate(BaseModel):
    name: str
    description: str | None = None
    items: list[ChecklistTemplateItemCreate] = []


class ChecklistTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ChecklistTemplateResponse(BaseModel):
    id: int
    name: str
    description: str | None
    items: list[ChecklistTemplateItemResponse]

    model_config = ConfigDict(from_attributes=True)
