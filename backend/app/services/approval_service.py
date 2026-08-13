from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ApprovalStatus
from app.models.approval import Approval
from app.models.approval_event import ApprovalEvent
from app.repositories.approval_event_repository import ApprovalEventRepository
from app.repositories.approval_repository import ApprovalRepository
from app.schemas.approval import ApprovalCreate, ApprovalTransition

# Default workflow a feature can rely on; not a hard DB-level constraint —
# see app/services/approval_service.py's ApprovalService docstring.
ALLOWED_TRANSITIONS: dict[ApprovalStatus, set[ApprovalStatus]] = {
    ApprovalStatus.DRAFT: {ApprovalStatus.SUBMITTED},
    ApprovalStatus.SUBMITTED: {ApprovalStatus.UNDER_REVIEW},
    ApprovalStatus.UNDER_REVIEW: {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED},
    ApprovalStatus.APPROVED: {ApprovalStatus.CLOSED},
    ApprovalStatus.REJECTED: {ApprovalStatus.SUBMITTED},
}


class ApprovalService:
    """Generic draft->submitted->under_review->approved/rejected->closed state
    machine. The allowed-transition map above is a sensible default, not a
    business rule baked into the primitive — a feature wrapping this service
    can layer stricter rules on top.
    """

    def __init__(self, db: AsyncSession):
        self.repo = ApprovalRepository(db)
        self.event_repo = ApprovalEventRepository(db)

    async def create(self, data: ApprovalCreate) -> Approval:
        approval = Approval(entity_type=data.entity_type, entity_id=data.entity_id)
        approval = await self.repo.create(approval)
        await self.event_repo.create(
            ApprovalEvent(approval_id=approval.id, from_status=None, to_status=approval.status)
        )
        return approval

    async def get(self, approval_id: int) -> Approval:
        approval = await self.repo.get_by_id(approval_id)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found")
        return approval

    async def get_all(self) -> list[Approval]:
        return await self.repo.get_all()

    async def get_by_entity(self, entity_type: str, entity_id: int) -> list[Approval]:
        return await self.repo.get_by_entity(entity_type, entity_id)

    async def get_events(self, approval_id: int) -> list[ApprovalEvent]:
        await self.get(approval_id)
        return await self.event_repo.get_by_approval(approval_id)

    async def submit(self, approval_id: int, data: ApprovalTransition) -> Approval:
        return await self._transition(approval_id, ApprovalStatus.SUBMITTED, data)

    async def review(self, approval_id: int, data: ApprovalTransition) -> Approval:
        approval = await self._transition(approval_id, ApprovalStatus.UNDER_REVIEW, data)
        return await self.repo.update(approval, {"current_assignee": data.actor})

    async def approve(self, approval_id: int, data: ApprovalTransition) -> Approval:
        approval = await self._transition(approval_id, ApprovalStatus.APPROVED, data)
        return await self.repo.update(approval, {"current_assignee": None})

    async def reject(self, approval_id: int, data: ApprovalTransition) -> Approval:
        approval = await self._transition(approval_id, ApprovalStatus.REJECTED, data)
        return await self.repo.update(approval, {"current_assignee": None})

    async def close(self, approval_id: int, data: ApprovalTransition) -> Approval:
        return await self._transition(approval_id, ApprovalStatus.CLOSED, data)

    async def _transition(
        self, approval_id: int, to_status: ApprovalStatus, data: ApprovalTransition
    ) -> Approval:
        approval = await self.get(approval_id)
        allowed = ALLOWED_TRANSITIONS.get(approval.status, set())
        if to_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from {approval.status} to {to_status}",
            )

        from_status = approval.status
        approval = await self.repo.update(
            approval, {"status": to_status, "updated_at": datetime.now(UTC)}
        )

        await self.event_repo.create(
            ApprovalEvent(
                approval_id=approval.id,
                from_status=from_status,
                to_status=to_status,
                actor=data.actor,
                comment=data.comment,
            )
        )
        return approval
