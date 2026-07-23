from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room
from app.repositories.floor_repository import FloorRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.room import RoomCreate, RoomUpdate


class RoomService:
    def __init__(self, db: AsyncSession):
        self.repo = RoomRepository(db)
        self.floor_repo = FloorRepository(db)

    async def _ensure_floor_exists(self, floor_id: int) -> None:
        floor = await self.floor_repo.get_by_id(floor_id)
        if not floor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Floor {floor_id} not found"
            )

    async def create_room(self, data: RoomCreate) -> Room:
        await self._ensure_floor_exists(data.floor_id)
        room = Room(**data.model_dump())
        return await self.repo.create(room)

    async def get_room(self, room_id: int) -> Room:
        room = await self.repo.get_by_id(room_id)
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
        return room

    async def get_all_rooms(self) -> list[Room]:
        return await self.repo.get_all()

    async def get_rooms_by_floor(self, floor_id: int) -> list[Room]:
        await self._ensure_floor_exists(floor_id)
        return await self.repo.get_by_floor(floor_id)

    async def update_room(self, room_id: int, data: RoomUpdate) -> Room:
        room = await self.get_room(room_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(room, update_data)

    async def delete_room(self, room_id: int) -> None:
        room = await self.get_room(room_id)
        await self.repo.delete(room)
