from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import ChecklistInstanceStatus
from app.models.mixins import EntityRefMixin


class ChecklistInstance(EntityRefMixin, Base):
    __tablename__ = "checklist_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # SET NULL, not CASCADE: losing the template link doesn't invalidate an
    # instance — its items are a self-contained snapshot (see
    # ChecklistInstanceItem), mirroring StructuralElement.room_id.
    template_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("checklist_templates.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[ChecklistInstanceStatus] = mapped_column(
        Enum(ChecklistInstanceStatus, name="checklist_instance_status", native_enum=False),
        nullable=False,
        default=ChecklistInstanceStatus.NOT_STARTED,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    template = relationship("ChecklistTemplate")
    items = relationship(
        "ChecklistInstanceItem",
        back_populates="instance",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChecklistInstanceItem.sequence",
    )
