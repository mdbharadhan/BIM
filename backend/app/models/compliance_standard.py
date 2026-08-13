from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ComplianceStandard(Base):
    __tablename__ = "compliance_standards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    rules = relationship(
        "ComplianceRule",
        back_populates="standard",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
