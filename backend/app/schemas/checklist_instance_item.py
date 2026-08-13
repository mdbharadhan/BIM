from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import ChecklistItemState


class ChecklistInstanceItemComplete(BaseModel):
    state: ChecklistItemState
    evidence_ref: str | None = None
    completed_by: str | None = None
    notes: str | None = None


class ChecklistInstanceItemResponse(BaseModel):
    id: int
    instance_id: int
    template_item_id: int | None
    label: str
    sequence: int
    is_required: bool
    requires_evidence: bool
    state: ChecklistItemState
    evidence_ref: str | None
    completed_by: str | None
    completed_at: datetime | None
    notes: str | None

    model_config = ConfigDict(from_attributes=True)
