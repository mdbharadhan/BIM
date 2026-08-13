from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building


class BuildingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, building: Building) -> Building:
        self.db.add(building)
        await self.db.commit()
        await self.db.refresh(building)
        return building

    async def get_by_id(self, building_id: int) -> Building | None:
        result = await self.db.execute(select(Building).where(Building.id == building_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Building]:
        result = await self.db.execute(select(Building))
        return list(result.scalars().all())

    async def update(self, building: Building, data: dict) -> Building:
        for key, value in data.items():
            setattr(building, key, value)
        await self.db.commit()
        await self.db.refresh(building)
        return building

    async def delete(self, building: Building) -> None:
        await self.db.delete(building)
        await self.db.commit()
