from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    room_name: Mapped[str] = mapped_column(String, nullable=False)
    room_number: Mapped[str | None] = mapped_column(String, nullable=True)
    room_type: Mapped[str | None] = mapped_column(String, nullable=True)
    floor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("floors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    area: Mapped[float | None] = mapped_column(Float, nullable=True)
    occupancy: Mapped[int | None] = mapped_column(Integer, nullable=True)

    floor = relationship("Floor", back_populates="rooms")
    # No delete-orphan cascade here: deleting a Room must not delete elements
    # that reference it (an interior wall still belongs to the Floor even if
    # its Room disappears) — only room_id gets nulled out (see StructuralElement.room_id).
    structural_elements = relationship("StructuralElement", back_populates="room")
