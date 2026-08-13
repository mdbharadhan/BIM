from pydantic import BaseModel, ConfigDict


class ChecklistTemplateItemCreate(BaseModel):
    label: str
    sequence: int = 0
    is_required: bool = True
    requires_evidence: bool = False


class ChecklistTemplateItemResponse(BaseModel):
    id: int
    template_id: int
    label: str
    sequence: int
    is_required: bool
    requires_evidence: bool

    model_config = ConfigDict(from_attributes=True)
