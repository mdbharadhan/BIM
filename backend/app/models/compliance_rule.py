from sqlalchemy import Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import ComplianceOperator


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    standard_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("compliance_standards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    parameter_name: Mapped[str | None] = mapped_column(String, nullable=True)
    operator: Mapped[ComplianceOperator] = mapped_column(
        Enum(ComplianceOperator, name="compliance_operator", native_enum=False), nullable=False
    )
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)
    # Carries non-numeric rules (e.g. "Material Test Certificate must be
    # provided") that don't reduce to a threshold comparison.
    rule_text: Mapped[str | None] = mapped_column(String, nullable=True)

    standard = relationship("ComplianceStandard", back_populates="rules")
