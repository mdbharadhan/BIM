from datetime import datetime

from pydantic import BaseModel

from app.domain.audit import AuditType
from app.domain.enums import ApprovalStatus
from app.schemas.approval_event import ApprovalEventResponse
from app.schemas.mixins import EntityRef


class AuditCreate(EntityRef):
    """Raise (open) an audit against the entity being audited — a Room, a
    structural element, or a Room standing in for an entity type with no
    table yet (see docs/adr/0001-entity-reference-no-fk.md)."""


class AuditSubmit(BaseModel):
    audit_type: AuditType
    auditor: str | None = None
    notes: str | None = None


class AuditResponse(BaseModel):
    id: int
    entity_type: str | None
    entity_id: int | None
    status: ApprovalStatus
    current_assignee: str | None
    created_at: datetime
    updated_at: datetime
    audit_type: AuditType | None
    notes: str | None


class AuditEventResponse(ApprovalEventResponse):
    pass
