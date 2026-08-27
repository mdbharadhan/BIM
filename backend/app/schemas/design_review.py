from datetime import datetime

from pydantic import BaseModel

from app.domain.design_review import DesignReviewType
from app.domain.enums import ApprovalStatus
from app.schemas.approval_event import ApprovalEventResponse
from app.schemas.mixins import EntityRef


class DesignReviewCreate(EntityRef):
    """Raise (open) a design review against the artifact being reviewed —
    typically entity_type="document" pointing at the Document row under
    review (see docs/primitives/approval.md's Design QA example use)."""


class DesignReviewSubmit(BaseModel):
    review_type: DesignReviewType
    reviewer: str | None = None
    notes: str | None = None


class DesignReviewResponse(BaseModel):
    id: int
    entity_type: str | None
    entity_id: int | None
    status: ApprovalStatus
    current_assignee: str | None
    created_at: datetime
    updated_at: datetime
    review_type: DesignReviewType | None
    notes: str | None


class DesignReviewEventResponse(ApprovalEventResponse):
    pass
