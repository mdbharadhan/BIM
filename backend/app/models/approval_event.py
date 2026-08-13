from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import ApprovalStatus


class ApprovalEvent(Base):
    __tablename__ = "approval_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    approval_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("approvals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Nullable: the first event (creation -> draft) has no prior status.
    from_status: Mapped[ApprovalStatus | None] = mapped_column(
        Enum(ApprovalStatus, name="approval_status", native_enum=False), nullable=True
    )
    to_status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, name="approval_status", native_enum=False), nullable=False
    )
    actor: Mapped[str | None] = mapped_column(String, nullable=True)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )

    approval = relationship("Approval", back_populates="events")
