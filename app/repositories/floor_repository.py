from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.floor import Floor


class FloorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, floor: Floor) -> Floor:
        self.db.add(floor)
        await self.db.commit()
        await self.db.refresh(floor)
        return floor

    async def get_by_id(self, floor_id: int) -> Floor | None:
        result = await self.db.execute(select(Floor).where(Floor.id == floor_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Floor]:
        result = await self.db.execute(select(Floor))
        return list(result.scalars().all())

    async def get_by_building(self, building_id: int) -> list[Floor]:
        result = await self.db.execute(select(Floor).where(Floor.building_id == building_id))
        return list(result.scalars().all())

    async def update(self, floor: Floor, data: dict) -> Floor:
        for key, value in data.items():
            setattr(floor, key, value)
        await self.db.commit()
        await self.db.refresh(floor)
        return floor

    async def delete(self, floor: Floor) -> None:
        await self.db.delete(floor)
        await self.db.commit()
