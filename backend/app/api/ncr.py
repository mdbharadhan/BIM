from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.approval import Approval
from app.models.approval_event import ApprovalEvent
from app.schemas.approval import ApprovalTransition
from app.schemas.ncr import NCRCreate, NCREventResponse, NCRResponse
from app.services.ncr_service import NCRService

router = APIRouter(tags=["NCRs"])


@router.post("/ncrs", response_model=NCRResponse, status_code=201)
async def raise_ncr(data: NCRCreate, db: AsyncSession = Depends(get_db)) -> Approval:
    return await NCRService(db).raise_ncr(data)


@router.get("/ncrs", response_model=list[NCRResponse])
async def list_ncrs(db: AsyncSession = Depends(get_db)) -> list[Approval]:
    return await NCRService(db).get_all()


@router.get("/ncrs/{ncr_id}", response_model=NCRResponse)
async def get_ncr(ncr_id: int, db: AsyncSession = Depends(get_db)) -> Approval:
    return await NCRService(db).get(ncr_id)


@router.get("/ncrs/{ncr_id}/events", response_model=list[NCREventResponse])
async def list_ncr_events(ncr_id: int, db: AsyncSession = Depends(get_db)) -> list[ApprovalEvent]:
    return await NCRService(db).events(ncr_id)


@router.post("/ncrs/{ncr_id}/submit", response_model=NCRResponse)
async def submit_ncr(
    ncr_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await NCRService(db).submit(ncr_id, data)


@router.post("/ncrs/{ncr_id}/review", response_model=NCRResponse)
async def review_ncr(
    ncr_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await NCRService(db).review(ncr_id, data)


@router.post("/ncrs/{ncr_id}/approve", response_model=NCRResponse)
async def approve_ncr(
    ncr_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await NCRService(db).approve(ncr_id, data)


@router.post("/ncrs/{ncr_id}/reject", response_model=NCRResponse)
async def reject_ncr(
    ncr_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await NCRService(db).reject(ncr_id, data)


@router.post("/ncrs/{ncr_id}/close", response_model=NCRResponse)
async def close_ncr(
    ncr_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await NCRService(db).close(ncr_id, data)


@router.get("/entities/{entity_type}/{entity_id}/ncrs", response_model=list[NCRResponse])
async def get_ncrs_by_entity(
    entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db)
) -> list[Approval]:
    return await NCRService(db).get_by_entity(entity_type, entity_id)
