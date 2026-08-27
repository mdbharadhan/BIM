"""NCR (Non-Conformance Report) workflow — a thin layer over the Approval
primitive's state machine, not a new primitive.

An NCR is raised against whatever real-world thing it concerns via the same
Entity Reference every primitive uses (see docs/adr/0001-entity-reference-no-fk.md).
Its draft -> submitted -> under_review -> approved/rejected -> closed lifecycle
and audit trail are exactly Approval's; the only thing this layer adds is a
feature-level rule ApprovalService's own docstring explicitly invites: an NCR
without a description of the non-conformance, or a rejection without a
reason, isn't useful, so `comment` is required on submit and reject.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval
from app.models.approval_event import ApprovalEvent
from app.schemas.approval import ApprovalCreate, ApprovalTransition
from app.schemas.ncr import NCRCreate
from app.services.approval_service import ApprovalService


class NCRService:
    def __init__(self, db: AsyncSession):
        self.approvals = ApprovalService(db)

    async def raise_ncr(self, data: NCRCreate) -> Approval:
        return await self.approvals.create(
            ApprovalCreate(entity_type=data.entity_type, entity_id=data.entity_id)
        )

    async def get(self, ncr_id: int) -> Approval:
        return await self.approvals.get(ncr_id)

    async def get_all(self) -> list[Approval]:
        return await self.approvals.get_all()

    async def get_by_entity(self, entity_type: str, entity_id: int) -> list[Approval]:
        return await self.approvals.get_by_entity(entity_type, entity_id)

    async def events(self, ncr_id: int) -> list[ApprovalEvent]:
        return await self.approvals.get_events(ncr_id)

    async def submit(self, ncr_id: int, data: ApprovalTransition) -> Approval:
        self._require_comment(data, "An NCR must describe the non-conformance when submitted")
        return await self.approvals.submit(ncr_id, data)

    async def review(self, ncr_id: int, data: ApprovalTransition) -> Approval:
        return await self.approvals.review(ncr_id, data)

    async def approve(self, ncr_id: int, data: ApprovalTransition) -> Approval:
        return await self.approvals.approve(ncr_id, data)

    async def reject(self, ncr_id: int, data: ApprovalTransition) -> Approval:
        self._require_comment(data, "A rejected NCR must include a reason")
        return await self.approvals.reject(ncr_id, data)

    async def close(self, ncr_id: int, data: ApprovalTransition) -> Approval:
        return await self.approvals.close(ncr_id, data)

    def _require_comment(self, data: ApprovalTransition, message: str) -> None:
        if not data.comment or not data.comment.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
