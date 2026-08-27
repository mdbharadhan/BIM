from app.schemas.approval import ApprovalResponse
from app.schemas.approval_event import ApprovalEventResponse
from app.schemas.mixins import EntityRef


class NCRCreate(EntityRef):
    """Raise an NCR against the entity it concerns (a Room, a structural
    element, or a Room standing in for an entity type with no table yet —
    see docs/adr/0001-entity-reference-no-fk.md)."""


class NCRResponse(ApprovalResponse):
    pass


class NCREventResponse(ApprovalEventResponse):
    pass
