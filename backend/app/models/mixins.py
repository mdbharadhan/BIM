from typing import Any

from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class EntityRefMixin:
    """Generic, unenforced pointer to any real-world entity (a Room, a Building,
    or a table owned by a future feature — an NCR, a material delivery — that
    doesn't exist yet). See CONTEXT.md's "Entity Reference" entry.

    entity_id assumes an Integer primary key, matching every table in this repo.
    entity_type is a lowercase snake_case singular noun matching the target
    concept (e.g. "room", "structural_element", "material_delivery") — not
    enforced by the database, since target tables may not exist yet.

    Columns are nullable here; primitives that require an attachment enforce
    that at the Pydantic layer (see app.schemas.mixins.EntityRef) instead of
    the database, so a primitive that allows unattached records (Document) can
    reuse the same columns without a second mixin.
    """

    entity_type: Mapped[str | None] = mapped_column(String, nullable=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    @declared_attr.directive
    def __table_args__(cls: Any) -> tuple[Index, ...]:  # noqa: N805
        return (Index(f"ix_{cls.__tablename__}_entity", "entity_type", "entity_id"),)
