import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.approval import ApprovalTransition
from app.schemas.ncr import NCRCreate
from app.services.ncr_service import NCRService


async def _raised(service: NCRService):
    return await service.raise_ncr(NCRCreate(entity_type="room", entity_id=1))


async def test_raise_ncr_defaults_to_draft(db_session: AsyncSession):
    service = NCRService(db_session)
    ncr = await _raised(service)
    assert ncr.status == "draft"
    assert ncr.entity_type == "room"


async def test_submit_without_comment_is_rejected(db_session: AsyncSession):
    service = NCRService(db_session)
    ncr = await _raised(service)

    with pytest.raises(HTTPException) as exc_info:
        await service.submit(ncr.id, ApprovalTransition(actor="qa@example.com"))
    assert exc_info.value.status_code == 400


async def test_submit_with_comment_transitions(db_session: AsyncSession):
    service = NCRService(db_session)
    ncr = await _raised(service)

    submitted = await service.submit(
        ncr.id, ApprovalTransition(actor="qa@example.com", comment="Rebar cover deficient")
    )
    assert submitted.status == "submitted"


async def test_reject_without_comment_is_rejected(db_session: AsyncSession):
    service = NCRService(db_session)
    ncr = await _raised(service)
    await service.submit(ncr.id, ApprovalTransition(comment="deficient cover"))
    await service.review(ncr.id, ApprovalTransition(actor="reviewer@example.com"))

    with pytest.raises(HTTPException) as exc_info:
        await service.reject(ncr.id, ApprovalTransition(actor="reviewer@example.com"))
    assert exc_info.value.status_code == 400


async def test_full_ncr_lifecycle(db_session: AsyncSession):
    service = NCRService(db_session)
    ncr = await _raised(service)

    await service.submit(ncr.id, ApprovalTransition(actor="qa@example.com", comment="found it"))
    await service.review(ncr.id, ApprovalTransition(actor="reviewer@example.com"))
    approved = await service.approve(ncr.id, ApprovalTransition(actor="reviewer@example.com"))
    assert approved.status == "approved"

    closed = await service.close(ncr.id, ApprovalTransition(actor="qa@example.com"))
    assert closed.status == "closed"

    events = await service.events(ncr.id)
    assert [e.to_status for e in events] == [
        "draft",
        "submitted",
        "under_review",
        "approved",
        "closed",
    ]
