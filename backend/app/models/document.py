from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.enums import DocumentStatus
from app.models.mixins import EntityRefMixin


class Document(EntityRefMixin, Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Stable grouping key shared by every version of "the same" document — set
    # to the row's own id on first upload. Not a FK: it's a label, not a link.
    # A bare supersedes_id chain can only walk backward from a known row, so
    # can't answer "what's current" in O(1) if the caller only has an old id.
    family_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status", native_enum=False),
        nullable=False,
        default=DocumentStatus.CURRENT,
        index=True,
    )
    supersedes_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )
    file_ref: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
