from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.approval import Approval
from app.models.approval_event import ApprovalEvent
from app.schemas.approval import ApprovalCreate, ApprovalResponse, ApprovalTransition
from app.schemas.approval_event import ApprovalEventResponse
from app.services.approval_service import ApprovalService

router = APIRouter(tags=["Approvals"])


@router.post("/approvals", response_model=ApprovalResponse, status_code=201)
async def create_approval(
    data: ApprovalCreate, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await ApprovalService(db).create(data)


@router.get("/approvals", response_model=list[ApprovalResponse])
async def list_approvals(db: AsyncSession = Depends(get_db)) -> list[Approval]:
    return await ApprovalService(db).get_all()


@router.get("/approvals/{approval_id}", response_model=ApprovalResponse)
async def get_approval(approval_id: int, db: AsyncSession = Depends(get_db)) -> Approval:
    return await ApprovalService(db).get(approval_id)


@router.get("/approvals/{approval_id}/events", response_model=list[ApprovalEventResponse])
async def list_approval_events(
    approval_id: int, db: AsyncSession = Depends(get_db)
) -> list[ApprovalEvent]:
    return await ApprovalService(db).get_events(approval_id)


@router.post("/approvals/{approval_id}/submit", response_model=ApprovalResponse)
async def submit_approval(
    approval_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await ApprovalService(db).submit(approval_id, data)


@router.post("/approvals/{approval_id}/review", response_model=ApprovalResponse)
async def review_approval(
    approval_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await ApprovalService(db).review(approval_id, data)


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_approval(
    approval_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await ApprovalService(db).approve(approval_id, data)


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_approval(
    approval_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await ApprovalService(db).reject(approval_id, data)


@router.post("/approvals/{approval_id}/close", response_model=ApprovalResponse)
async def close_approval(
    approval_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> Approval:
    return await ApprovalService(db).close(approval_id, data)


@router.get("/entities/{entity_type}/{entity_id}/approvals", response_model=list[ApprovalResponse])
async def get_approvals_by_entity(
    entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db)
) -> list[Approval]:
    return await ApprovalService(db).get_by_entity(entity_type, entity_id)
