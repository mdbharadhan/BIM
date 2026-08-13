from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Floor(Base):
    __tablename__ = "floors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    floor_name: Mapped[str] = mapped_column(String, nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False)
    building_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True
    )

    building = relationship("Building", back_populates="floors")
    rooms = relationship(
        "Room",
        back_populates="floor",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    structural_elements = relationship(
        "StructuralElement",
        back_populates="floor",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
