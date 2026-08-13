from pydantic import BaseModel


class EntityRef(BaseModel):
    """Required entity_type/entity_id pair for primitives that must always be
    attached to something (Checklist, Approval, Compliance). Document declares
    these two fields directly as optional instead of inheriting this, since it
    is the one primitive that supports unattached, project-global records.
    """

    entity_type: str
    entity_id: int
