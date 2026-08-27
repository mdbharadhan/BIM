from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.approval_event import ApprovalEvent
from app.schemas.approval import ApprovalTransition
from app.schemas.audit import AuditCreate, AuditEventResponse, AuditResponse, AuditSubmit
from app.services.audit_service import AuditService

router = APIRouter(tags=["Audits"])


@router.post("/audits", response_model=AuditResponse, status_code=201)
async def raise_audit(data: AuditCreate, db: AsyncSession = Depends(get_db)) -> AuditResponse:
    return await AuditService(db).raise_audit(data)


@router.get("/audits", response_model=list[AuditResponse])
async def list_audits(db: AsyncSession = Depends(get_db)) -> list[AuditResponse]:
    return await AuditService(db).get_all()


@router.get("/audits/{audit_id}", response_model=AuditResponse)
async def get_audit(audit_id: int, db: AsyncSession = Depends(get_db)) -> AuditResponse:
    return await AuditService(db).get(audit_id)


@router.get("/audits/{audit_id}/events", response_model=list[AuditEventResponse])
async def list_audit_events(
    audit_id: int, db: AsyncSession = Depends(get_db)
) -> list[ApprovalEvent]:
    return await AuditService(db).events(audit_id)


@router.post("/audits/{audit_id}/submit", response_model=AuditResponse)
async def submit_audit(
    audit_id: int, data: AuditSubmit, db: AsyncSession = Depends(get_db)
) -> AuditResponse:
    return await AuditService(db).submit(audit_id, data)


@router.post("/audits/{audit_id}/review", response_model=AuditResponse)
async def review_audit(
    audit_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> AuditResponse:
    return await AuditService(db).review(audit_id, data)


@router.post("/audits/{audit_id}/approve", response_model=AuditResponse)
async def approve_audit(
    audit_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> AuditResponse:
    return await AuditService(db).approve(audit_id, data)


@router.post("/audits/{audit_id}/reject", response_model=AuditResponse)
async def reject_audit(
    audit_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> AuditResponse:
    return await AuditService(db).reject(audit_id, data)


@router.post("/audits/{audit_id}/close", response_model=AuditResponse)
async def close_audit(
    audit_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> AuditResponse:
    return await AuditService(db).close(audit_id, data)


@router.get("/entities/{entity_type}/{entity_id}/audits", response_model=list[AuditResponse])
async def get_audits_by_entity(
    entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db)
) -> list[AuditResponse]:
    return await AuditService(db).get_by_entity(entity_type, entity_id)
