import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ApprovalStatus
from app.schemas.approval import ApprovalCreate, ApprovalTransition
from app.services.approval_service import ApprovalService


async def test_reject_then_resubmit_allowed(db_session: AsyncSession):
    service = ApprovalService(db_session)
    approval = await service.create(ApprovalCreate(entity_type="room", entity_id=1))

    await service.submit(approval.id, ApprovalTransition())
    await service.review(approval.id, ApprovalTransition())
    approval = await service.reject(approval.id, ApprovalTransition(comment="not compliant"))
    assert approval.status == ApprovalStatus.REJECTED

    approval = await service.submit(approval.id, ApprovalTransition())
    assert approval.status == ApprovalStatus.SUBMITTED


async def test_invalid_transition_raises_400(db_session: AsyncSession):
    service = ApprovalService(db_session)
    approval = await service.create(ApprovalCreate(entity_type="room", entity_id=1))

    with pytest.raises(HTTPException) as exc_info:
        await service.approve(approval.id, ApprovalTransition())
    assert exc_info.value.status_code == 400


async def test_events_recorded_for_every_transition(db_session: AsyncSession):
    service = ApprovalService(db_session)
    approval = await service.create(ApprovalCreate(entity_type="room", entity_id=1))
    await service.submit(approval.id, ApprovalTransition(actor="engineer@example.com"))

    events = await service.get_events(approval.id)
    assert len(events) == 2
    assert events[0].from_status is None
    assert events[0].to_status == ApprovalStatus.DRAFT
    assert events[1].from_status == ApprovalStatus.DRAFT
    assert events[1].to_status == ApprovalStatus.SUBMITTED
    assert events[1].actor == "engineer@example.com"
