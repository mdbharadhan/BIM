from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChecklistTemplate(Base):
    __tablename__ = "checklist_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    items = relationship(
        "ChecklistTemplateItem",
        back_populates="template",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ChecklistTemplateItem.sequence",
    )
