from sqlalchemy import Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums import ElementType


class StructuralElement(Base):
    __tablename__ = "structural_elements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    element_name: Mapped[str] = mapped_column(String, nullable=False)
    element_type: Mapped[ElementType] = mapped_column(
        Enum(ElementType, name="element_type", native_enum=False), nullable=False
    )
    material: Mapped[str | None] = mapped_column(String, nullable=True)

    # floor_id is required; room_id is optional — some elements (exterior
    # walls, roof slabs) belong to a Floor but not to any specific Room.
    floor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("floors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    room_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True, index=True
    )

    dim_width: Mapped[float | None] = mapped_column(Float, nullable=True)
    dim_height: Mapped[float | None] = mapped_column(Float, nullable=True)
    dim_depth: Mapped[float | None] = mapped_column(Float, nullable=True)

    floor = relationship("Floor", back_populates="structural_elements")
    room = relationship("Room", back_populates="structural_elements")
