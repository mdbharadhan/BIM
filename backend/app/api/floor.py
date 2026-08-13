from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.floor import Floor
from app.schemas.floor import FloorCreate, FloorResponse, FloorUpdate
from app.services.floor_service import FloorService

router = APIRouter(tags=["Floors"])


@router.post("/floors", response_model=FloorResponse, status_code=201)
async def create_floor(data: FloorCreate, db: AsyncSession = Depends(get_db)) -> Floor:
    service = FloorService(db)
    return await service.create_floor(data)


@router.get("/floors", response_model=list[FloorResponse])
async def list_floors(db: AsyncSession = Depends(get_db)) -> list[Floor]:
    service = FloorService(db)
    return await service.get_all_floors()


@router.get("/floors/{floor_id}", response_model=FloorResponse)
async def get_floor(floor_id: int, db: AsyncSession = Depends(get_db)) -> Floor:
    service = FloorService(db)
    return await service.get_floor(floor_id)


@router.put("/floors/{floor_id}", response_model=FloorResponse)
async def update_floor(
    floor_id: int, data: FloorUpdate, db: AsyncSession = Depends(get_db)
) -> Floor:
    service = FloorService(db)
    return await service.update_floor(floor_id, data)


@router.delete("/floors/{floor_id}", status_code=204)
async def delete_floor(floor_id: int, db: AsyncSession = Depends(get_db)) -> None:
    service = FloorService(db)
    await service.delete_floor(floor_id)


@router.get("/buildings/{building_id}/floors", response_model=list[FloorResponse])
async def get_floors_by_building(
    building_id: int, db: AsyncSession = Depends(get_db)
) -> list[Floor]:
    service = FloorService(db)
    return await service.get_floors_by_building(building_id)
