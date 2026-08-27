import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.audit import AuditType
from app.schemas.approval import ApprovalTransition
from app.schemas.audit import AuditCreate, AuditSubmit
from app.services.audit_service import AuditService


async def _raised(service: AuditService):
    return await service.raise_audit(AuditCreate(entity_type="room", entity_id=1))


async def test_raise_audit_defaults_to_draft_with_no_audit_type(db_session: AsyncSession):
    service = AuditService(db_session)
    audit = await _raised(service)
    assert audit.status == "draft"
    assert audit.audit_type is None


async def test_submit_records_audit_type_and_notes(db_session: AsyncSession):
    service = AuditService(db_session)
    audit = await _raised(service)

    submitted = await service.submit(
        audit.id,
        AuditSubmit(audit_type=AuditType.REGULATORY, auditor="inspector@example.com", notes="ok"),
    )
    assert submitted.status == "submitted"
    assert submitted.audit_type is AuditType.REGULATORY
    assert submitted.notes == "ok"


async def test_get_reflects_the_latest_submission(db_session: AsyncSession):
    """Resubmission after rejection should update the reported audit_type."""
    service = AuditService(db_session)
    audit = await _raised(service)
    await service.submit(audit.id, AuditSubmit(audit_type=AuditType.INTERNAL))
    await service.review(audit.id, ApprovalTransition(actor="reviewer@example.com"))
    await service.reject(
        audit.id, ApprovalTransition(actor="reviewer@example.com", comment="incomplete")
    )
    await service.submit(audit.id, AuditSubmit(audit_type=AuditType.EXTERNAL, notes="redone"))

    current = await service.get(audit.id)
    assert current.audit_type is AuditType.EXTERNAL
    assert current.notes == "redone"


async def test_reject_without_comment_is_rejected(db_session: AsyncSession):
    service = AuditService(db_session)
    audit = await _raised(service)
    await service.submit(audit.id, AuditSubmit(audit_type=AuditType.INTERNAL))
    await service.review(audit.id, ApprovalTransition(actor="reviewer@example.com"))

    with pytest.raises(HTTPException) as exc_info:
        await service.reject(audit.id, ApprovalTransition(actor="reviewer@example.com"))
    assert exc_info.value.status_code == 400


async def test_full_audit_lifecycle(db_session: AsyncSession):
    service = AuditService(db_session)
    audit = await _raised(service)

    await service.submit(
        audit.id, AuditSubmit(audit_type=AuditType.CLIENT, auditor="qa@example.com")
    )
    await service.review(audit.id, ApprovalTransition(actor="reviewer@example.com"))
    approved = await service.approve(audit.id, ApprovalTransition(actor="reviewer@example.com"))
    assert approved.status == "approved"
    assert approved.audit_type is AuditType.CLIENT

    closed = await service.close(audit.id, ApprovalTransition(actor="qa@example.com"))
    assert closed.status == "closed"

    events = await service.events(audit.id)
    assert [e.to_status for e in events] == [
        "draft",
        "submitted",
        "under_review",
        "approved",
        "closed",
    ]
