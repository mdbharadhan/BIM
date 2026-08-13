from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.floor import Floor
from app.repositories.building_repository import BuildingRepository
from app.repositories.floor_repository import FloorRepository
from app.schemas.floor import FloorCreate, FloorUpdate


class FloorService:
    def __init__(self, db: AsyncSession):
        self.repo = FloorRepository(db)
        self.building_repo = BuildingRepository(db)

    async def _ensure_building_exists(self, building_id: int) -> None:
        building = await self.building_repo.get_by_id(building_id)
        if not building:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Building {building_id} not found",
            )

    async def create_floor(self, data: FloorCreate) -> Floor:
        await self._ensure_building_exists(data.building_id)
        floor = Floor(**data.model_dump())
        return await self.repo.create(floor)

    async def get_floor(self, floor_id: int) -> Floor:
        floor = await self.repo.get_by_id(floor_id)
        if not floor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found")
        return floor

    async def get_all_floors(self) -> list[Floor]:
        return await self.repo.get_all()

    async def get_floors_by_building(self, building_id: int) -> list[Floor]:
        await self._ensure_building_exists(building_id)
        return await self.repo.get_by_building(building_id)

    async def update_floor(self, floor_id: int, data: FloorUpdate) -> Floor:
        floor = await self.get_floor(floor_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(floor, update_data)

    async def delete_floor(self, floor_id: int) -> None:
        floor = await self.get_floor(floor_id)
        await self.repo.delete(floor)
