from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.structural_element import StructuralElement
from app.schemas.structural_element import (
    StructuralElementCreate,
    StructuralElementResponse,
    StructuralElementUpdate,
)
from app.services.structural_element_service import StructuralElementService

router = APIRouter(tags=["Structural Elements"])


@router.post("/structural-elements", response_model=StructuralElementResponse, status_code=201)
async def create_element(
    data: StructuralElementCreate, db: AsyncSession = Depends(get_db)
) -> StructuralElement:
    service = StructuralElementService(db)
    return await service.create_element(data)


@router.get("/structural-elements", response_model=list[StructuralElementResponse])
async def list_elements(db: AsyncSession = Depends(get_db)) -> list[StructuralElement]:
    service = StructuralElementService(db)
    return await service.get_all_elements()


@router.get("/structural-elements/{element_id}", response_model=StructuralElementResponse)
async def get_element(element_id: int, db: AsyncSession = Depends(get_db)) -> StructuralElement:
    service = StructuralElementService(db)
    return await service.get_element(element_id)


@router.put("/structural-elements/{element_id}", response_model=StructuralElementResponse)
async def update_element(
    element_id: int, data: StructuralElementUpdate, db: AsyncSession = Depends(get_db)
) -> StructuralElement:
    service = StructuralElementService(db)
    return await service.update_element(element_id, data)


@router.delete("/structural-elements/{element_id}", status_code=204)
async def delete_element(element_id: int, db: AsyncSession = Depends(get_db)) -> None:
    service = StructuralElementService(db)
    await service.delete_element(element_id)


@router.get("/rooms/{room_id}/elements", response_model=list[StructuralElementResponse])
async def get_elements_by_room(
    room_id: int, db: AsyncSession = Depends(get_db)
) -> list[StructuralElement]:
    service = StructuralElementService(db)
    return await service.get_elements_by_room(room_id)
