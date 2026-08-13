from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import ChecklistItemState


class ChecklistInstanceItem(Base):
    __tablename__ = "checklist_instance_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    instance_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("checklist_instances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Traceability only, not the source of truth for display — label/sequence/
    # is_required/requires_evidence below are copied from the template item at
    # instance-creation time, so editing the template later never rewrites an
    # already-completed instance's history.
    template_item_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("checklist_template_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    label: Mapped[str] = mapped_column(String, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requires_evidence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    state: Mapped[ChecklistItemState] = mapped_column(
        Enum(ChecklistItemState, name="checklist_item_state", native_enum=False),
        nullable=False,
        default=ChecklistItemState.PENDING,
    )
    evidence_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    completed_by: Mapped[str | None] = mapped_column(String, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    instance = relationship("ChecklistInstance", back_populates="items")
