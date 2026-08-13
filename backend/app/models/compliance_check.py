from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.enums import ComplianceResult
from app.models.mixins import EntityRefMixin


class ComplianceCheck(EntityRefMixin, Base):
    __tablename__ = "compliance_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # SET NULL, not CASCADE: a check's historical result must survive its rule
    # being edited or removed later — mirrors StructuralElement.room_id.
    rule_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("compliance_rules.id", ondelete="SET NULL"), nullable=True, index=True
    )
    measured_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    result: Mapped[ComplianceResult] = mapped_column(
        Enum(ComplianceResult, name="compliance_result", native_enum=False), nullable=False
    )
    checked_by: Mapped[str | None] = mapped_column(String, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
