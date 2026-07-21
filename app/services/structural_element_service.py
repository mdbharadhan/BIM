from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.structural_element import StructuralElement
from app.repositories.floor_repository import FloorRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.structural_element_repository import StructuralElementRepository
from app.schemas.structural_element import StructuralElementCreate, StructuralElementUpdate


class StructuralElementService:
    def __init__(self, db: AsyncSession):
        self.repo = StructuralElementRepository(db)
        self.room_repo = RoomRepository(db)
        self.floor_repo = FloorRepository(db)

    async def _validate_floor_and_room(self, floor_id: int, room_id: int | None) -> None:
        floor = await self.floor_repo.get_by_id(floor_id)
        if not floor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Floor {floor_id} not found"
            )

        if room_id is not None:
            room = await self.room_repo.get_by_id(room_id)
            if not room:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {room_id} not found"
                )
            if room.floor_id != floor_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="room_id does not belong to the given floor_id",
                )

    async def create_element(self, data: StructuralElementCreate) -> StructuralElement:
        await self._validate_floor_and_room(data.floor_id, data.room_id)
        element = StructuralElement(**data.model_dump())
        return await self.repo.create(element)

    async def get_element(self, element_id: int) -> StructuralElement:
        element = await self.repo.get_by_id(element_id)
        if not element:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Structural element not found"
            )
        return element

    async def get_all_elements(self) -> list[StructuralElement]:
        return await self.repo.get_all()

    async def get_elements_by_room(self, room_id: int) -> list[StructuralElement]:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {room_id} not found"
            )
        return await self.repo.get_by_room(room_id)

    async def update_element(
        self, element_id: int, data: StructuralElementUpdate
    ) -> StructuralElement:
        element = await self.get_element(element_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(element, update_data)

    async def delete_element(self, element_id: int) -> None:
        element = await self.get_element(element_id)
        await self.repo.delete(element)
