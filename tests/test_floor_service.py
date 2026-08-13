import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.room_repository import RoomRepository
from app.repositories.structural_element_repository import StructuralElementRepository
from app.schemas.building import BuildingCreate
from app.schemas.floor import FloorCreate, FloorUpdate
from app.schemas.room import RoomCreate
from app.schemas.structural_element import StructuralElementCreate
from app.services.building_service import BuildingService
from app.services.floor_service import FloorService
from app.services.room_service import RoomService
from app.services.structural_element_service import StructuralElementService


async def test_create_floor_with_valid_building_succeeds(db_session: AsyncSession):
    building_service = BuildingService(db_session)
    floor_service = FloorService(db_session)

    building = await building_service.create_building(BuildingCreate(name="Tower A"))
    floor = await floor_service.create_floor(
        FloorCreate(floor_name="Ground", floor_number=0, building_id=building.id)
    )

    assert floor.id is not None
    assert floor.building_id == building.id


async def test_create_floor_with_nonexistent_building_raises_404(db_session: AsyncSession):
    floor_service = FloorService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await floor_service.create_floor(
            FloorCreate(floor_name="Ground", floor_number=0, building_id=999)
        )
    assert exc_info.value.status_code == 404


async def test_delete_floor_cascades_to_rooms_and_elements(db_session: AsyncSession):
    building_service = BuildingService(db_session)
    floor_service = FloorService(db_session)
    room_service = RoomService(db_session)
    element_service = StructuralElementService(db_session)
    room_repo = RoomRepository(db_session)
    element_repo = StructuralElementRepository(db_session)

    building = await building_service.create_building(BuildingCreate(name="Tower A"))
    floor = await floor_service.create_floor(
        FloorCreate(floor_name="Ground", floor_number=0, building_id=building.id)
    )
    room = await room_service.create_room(RoomCreate(room_name="Lobby", floor_id=floor.id))
    element = await element_service.create_element(
        StructuralElementCreate(element_name="Ext Wall", element_type="wall", floor_id=floor.id)
    )

    await floor_service.delete_floor(floor.id)

    assert await room_repo.get_by_id(room.id) is None
    assert await element_repo.get_by_id(element.id) is None


async def test_get_floor_not_found_raises_404(db_session: AsyncSession):
    floor_service = FloorService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await floor_service.get_floor(999)
    assert exc_info.value.status_code == 404


async def test_update_floor_not_found_raises_404(db_session: AsyncSession):
    floor_service = FloorService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await floor_service.update_floor(999, FloorUpdate(floor_number=5))
    assert exc_info.value.status_code == 404


async def test_delete_floor_not_found_raises_404(db_session: AsyncSession):
    floor_service = FloorService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await floor_service.delete_floor(999)
    assert exc_info.value.status_code == 404
