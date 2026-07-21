import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.floor_repository import FloorRepository
from app.schemas.building import BuildingCreate, BuildingUpdate
from app.schemas.floor import FloorCreate
from app.services.building_service import BuildingService
from app.services.floor_service import FloorService


async def test_create_building_assigns_id(db_session: AsyncSession):
    service = BuildingService(db_session)
    building = await service.create_building(BuildingCreate(name="Tower A", address="123 Main"))
    assert building.id is not None
    assert building.name == "Tower A"


async def test_get_building_not_found_raises_404(db_session: AsyncSession):
    service = BuildingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_building(999)
    assert exc_info.value.status_code == 404


async def test_update_building_not_found_raises_404(db_session: AsyncSession):
    service = BuildingService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await service.update_building(999, BuildingUpdate(name="New Name"))
    assert exc_info.value.status_code == 404


async def test_delete_building_cascades_to_floors(db_session: AsyncSession):
    building_service = BuildingService(db_session)
    floor_service = FloorService(db_session)
    floor_repo = FloorRepository(db_session)

    building = await building_service.create_building(BuildingCreate(name="Tower A"))
    floor = await floor_service.create_floor(
        FloorCreate(floor_name="Ground", floor_number=0, building_id=building.id)
    )

    await building_service.delete_building(building.id)

    assert await floor_repo.get_by_id(floor.id) is None
