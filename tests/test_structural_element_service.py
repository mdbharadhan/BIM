import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.building import BuildingCreate
from app.schemas.floor import FloorCreate
from app.schemas.room import RoomCreate
from app.schemas.structural_element import StructuralElementCreate
from app.services.building_service import BuildingService
from app.services.floor_service import FloorService
from app.services.room_service import RoomService
from app.services.structural_element_service import StructuralElementService


async def _make_floor(db_session: AsyncSession, name: str = "Ground"):
    building = await BuildingService(db_session).create_building(BuildingCreate(name="Tower A"))
    return await FloorService(db_session).create_floor(
        FloorCreate(floor_name=name, floor_number=0, building_id=building.id)
    )


async def test_create_element_without_room_succeeds(db_session: AsyncSession):
    floor = await _make_floor(db_session)
    service = StructuralElementService(db_session)

    element = await service.create_element(
        StructuralElementCreate(element_name="Ext Wall", element_type="wall", floor_id=floor.id)
    )

    assert element.id is not None
    assert element.room_id is None


async def test_create_element_with_matching_room_succeeds(db_session: AsyncSession):
    floor = await _make_floor(db_session)
    room = await RoomService(db_session).create_room(
        RoomCreate(room_name="Lobby", floor_id=floor.id)
    )
    service = StructuralElementService(db_session)

    element = await service.create_element(
        StructuralElementCreate(
            element_name="Interior Wall",
            element_type="wall",
            floor_id=floor.id,
            room_id=room.id,
        )
    )

    assert element.room_id == room.id


async def test_create_element_with_nonexistent_floor_raises_404(db_session: AsyncSession):
    service = StructuralElementService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_element(
            StructuralElementCreate(element_name="Wall", element_type="wall", floor_id=999)
        )
    assert exc_info.value.status_code == 404


async def test_create_element_with_nonexistent_room_raises_404(db_session: AsyncSession):
    floor = await _make_floor(db_session)
    service = StructuralElementService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_element(
            StructuralElementCreate(
                element_name="Wall", element_type="wall", floor_id=floor.id, room_id=999
            )
        )
    assert exc_info.value.status_code == 404


async def test_create_element_with_room_from_different_floor_raises_400(db_session: AsyncSession):
    floor_a = await _make_floor(db_session, "Floor A")
    floor_b = await _make_floor(db_session, "Floor B")
    room_on_a = await RoomService(db_session).create_room(
        RoomCreate(room_name="Lobby", floor_id=floor_a.id)
    )
    service = StructuralElementService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_element(
            StructuralElementCreate(
                element_name="Wall",
                element_type="wall",
                floor_id=floor_b.id,
                room_id=room_on_a.id,
            )
        )
    assert exc_info.value.status_code == 400
