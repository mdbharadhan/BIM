from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomResponse, RoomUpdate
from app.services.room_service import RoomService

router = APIRouter(tags=["Rooms"])


@router.post("/rooms", response_model=RoomResponse, status_code=201)
async def create_room(data: RoomCreate, db: AsyncSession = Depends(get_db)) -> Room:
    service = RoomService(db)
    return await service.create_room(data)


@router.get("/rooms", response_model=list[RoomResponse])
async def list_rooms(db: AsyncSession = Depends(get_db)) -> list[Room]:
    service = RoomService(db)
    return await service.get_all_rooms()


@router.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)) -> Room:
    service = RoomService(db)
    return await service.get_room(room_id)


@router.put("/rooms/{room_id}", response_model=RoomResponse)
async def update_room(room_id: int, data: RoomUpdate, db: AsyncSession = Depends(get_db)) -> Room:
    service = RoomService(db)
    return await service.update_room(room_id, data)


@router.delete("/rooms/{room_id}", status_code=204)
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db)) -> None:
    service = RoomService(db)
    await service.delete_room(room_id)


@router.get("/floors/{floor_id}/rooms", response_model=list[RoomResponse])
async def get_rooms_by_floor(floor_id: int, db: AsyncSession = Depends(get_db)) -> list[Room]:
    service = RoomService(db)
    return await service.get_rooms_by_floor(floor_id)
