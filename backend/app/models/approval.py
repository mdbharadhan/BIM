from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import ApprovalStatus
from app.models.mixins import EntityRefMixin


class Approval(EntityRefMixin, Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, name="approval_status", native_enum=False),
        nullable=False,
        default=ApprovalStatus.DRAFT,
    )
    # Set alongside the transition into under_review; querying "approvals
    # assigned to me right now" off the event log alone doesn't scale.
    current_assignee: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    events = relationship(
        "ApprovalEvent",
        back_populates="approval",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ApprovalEvent.created_at",
    )
