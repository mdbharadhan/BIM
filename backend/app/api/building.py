from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.building import Building
from app.schemas.building import BuildingCreate, BuildingResponse, BuildingUpdate
from app.services.building_service import BuildingService

router = APIRouter(tags=["Buildings"])


@router.post("/buildings", response_model=BuildingResponse, status_code=201)
async def create_building(data: BuildingCreate, db: AsyncSession = Depends(get_db)) -> Building:
    service = BuildingService(db)
    return await service.create_building(data)


@router.get("/buildings", response_model=list[BuildingResponse])
async def list_buildings(db: AsyncSession = Depends(get_db)) -> list[Building]:
    service = BuildingService(db)
    return await service.get_all_buildings()


@router.get("/buildings/{building_id}", response_model=BuildingResponse)
async def get_building(building_id: int, db: AsyncSession = Depends(get_db)) -> Building:
    service = BuildingService(db)
    return await service.get_building(building_id)


@router.put("/buildings/{building_id}", response_model=BuildingResponse)
async def update_building(
    building_id: int, data: BuildingUpdate, db: AsyncSession = Depends(get_db)
) -> Building:
    service = BuildingService(db)
    return await service.update_building(building_id, data)


@router.delete("/buildings/{building_id}", status_code=204)
async def delete_building(building_id: int, db: AsyncSession = Depends(get_db)) -> None:
    service = BuildingService(db)
    await service.delete_building(building_id)
