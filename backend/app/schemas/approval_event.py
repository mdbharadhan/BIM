from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import ApprovalStatus


class ApprovalEventResponse(BaseModel):
    id: int
    approval_id: int
    from_status: ApprovalStatus | None
    to_status: ApprovalStatus
    actor: str | None
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
