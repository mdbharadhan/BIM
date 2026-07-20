from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.building import Building
from app.repositories.building_repository import BuildingRepository
from app.schemas.building import BuildingCreate, BuildingUpdate


class BuildingService:
    def __init__(self, db: AsyncSession):
        self.repo = BuildingRepository(db)

    async def create_building(self, data: BuildingCreate) -> Building:
        building = Building(**data.model_dump())
        return await self.repo.create(building)

    async def get_building(self, building_id: int) -> Building:
        building = await self.repo.get_by_id(building_id)
        if not building:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
        return building

    async def get_all_buildings(self) -> list[Building]:
        return await self.repo.get_all()

    async def update_building(self, building_id: int, data: BuildingUpdate) -> Building:
        building = await self.get_building(building_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(building, update_data)

    async def delete_building(self, building_id: int) -> None:
        building = await self.get_building(building_id)
        await self.repo.delete(building)
