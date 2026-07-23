from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.structural_element import StructuralElement


class StructuralElementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, element: StructuralElement) -> StructuralElement:
        self.db.add(element)
        await self.db.commit()
        await self.db.refresh(element)
        return element

    async def get_by_id(self, element_id: int) -> StructuralElement | None:
        result = await self.db.execute(
            select(StructuralElement).where(StructuralElement.id == element_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[StructuralElement]:
        result = await self.db.execute(select(StructuralElement))
        return list(result.scalars().all())

    async def get_by_room(self, room_id: int) -> list[StructuralElement]:
        result = await self.db.execute(
            select(StructuralElement).where(StructuralElement.room_id == room_id)
        )
        return list(result.scalars().all())

    async def get_by_floor(self, floor_id: int) -> list[StructuralElement]:
        result = await self.db.execute(
            select(StructuralElement).where(StructuralElement.floor_id == floor_id)
        )
        return list(result.scalars().all())

    async def update(self, element: StructuralElement, data: dict) -> StructuralElement:
        for key, value in data.items():
            setattr(element, key, value)
        await self.db.commit()
        await self.db.refresh(element)
        return element

    async def delete(self, element: StructuralElement) -> None:
        await self.db.delete(element)
        await self.db.commit()
