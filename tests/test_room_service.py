import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.structural_element_repository import StructuralElementRepository
from app.schemas.building import BuildingCreate
from app.schemas.floor import FloorCreate
from app.schemas.room import RoomCreate
from app.schemas.structural_element import StructuralElementCreate
from app.services.building_service import BuildingService
from app.services.floor_service import FloorService
from app.services.room_service import RoomService
from app.services.structural_element_service import StructuralElementService


async def _make_floor(db_session: AsyncSession):
    building = await BuildingService(db_session).create_building(BuildingCreate(name="Tower A"))
    return await FloorService(db_session).create_floor(
        FloorCreate(floor_name="Ground", floor_number=0, building_id=building.id)
    )


async def test_create_room_with_valid_floor_succeeds(db_session: AsyncSession):
    floor = await _make_floor(db_session)
    room_service = RoomService(db_session)

    room = await room_service.create_room(RoomCreate(room_name="Lobby", floor_id=floor.id))

    assert room.id is not None
    assert room.floor_id == floor.id


async def test_create_room_with_nonexistent_floor_raises_404(db_session: AsyncSession):
    room_service = RoomService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await room_service.create_room(RoomCreate(room_name="Lobby", floor_id=999))
    assert exc_info.value.status_code == 404


async def test_delete_room_does_not_cascade_to_elements(db_session: AsyncSession):
    floor = await _make_floor(db_session)
    room_service = RoomService(db_session)
    element_service = StructuralElementService(db_session)
    element_repo = StructuralElementRepository(db_session)

    room = await room_service.create_room(RoomCreate(room_name="Lobby", floor_id=floor.id))
    element = await element_service.create_element(
        StructuralElementCreate(
            element_name="Interior Wall",
            element_type="wall",
            floor_id=floor.id,
            room_id=room.id,
        )
    )

    await room_service.delete_room(room.id)

    refreshed = await element_repo.get_by_id(element.id)
    assert refreshed is not None
    assert refreshed.room_id is None
