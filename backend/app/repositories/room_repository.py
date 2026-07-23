from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room


class RoomRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, room: Room) -> Room:
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def get_by_id(self, room_id: int) -> Room | None:
        result = await self.db.execute(select(Room).where(Room.id == room_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Room]:
        result = await self.db.execute(select(Room))
        return list(result.scalars().all())

    async def get_by_floor(self, floor_id: int) -> list[Room]:
        result = await self.db.execute(select(Room).where(Room.floor_id == floor_id))
        return list(result.scalars().all())

    async def update(self, room: Room, data: dict) -> Room:
        for key, value in data.items():
            setattr(room, key, value)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def delete(self, room: Room) -> None:
        await self.db.delete(room)
        await self.db.commit()
