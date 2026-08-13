from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import ApprovalStatus
from app.schemas.mixins import EntityRef


class ApprovalCreate(EntityRef):
    pass


class ApprovalTransition(BaseModel):
    actor: str | None = None
    comment: str | None = None


class ApprovalResponse(BaseModel):
    id: int
    entity_type: str | None
    entity_id: int | None
    status: ApprovalStatus
    current_assignee: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
