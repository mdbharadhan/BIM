"""Audit workflow — a thin layer over the Approval primitive's state machine,
not a new primitive.

An audit is raised against whatever entity it concerns via the same Entity
Reference every primitive uses (see docs/adr/0001-entity-reference-no-fk.md).
Its draft -> submitted -> under_review -> approved/rejected -> closed
lifecycle and audit trail are exactly Approval's. audit_type/auditor/notes
have no home on the Approval row itself (see app.domain.audit's module
docstring), so they travel inside the submit transition's comment and are
parsed back out of the event history for display. As with NCR, a rejection
must include a reason.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.audit import format_submission_comment, parse_submission_comment
from app.domain.enums import ApprovalStatus
from app.models.approval import Approval
from app.models.approval_event import ApprovalEvent
from app.schemas.approval import ApprovalCreate, ApprovalTransition
from app.schemas.audit import AuditCreate, AuditResponse, AuditSubmit
from app.services.approval_service import ApprovalService


class AuditService:
    def __init__(self, db: AsyncSession):
        self.approvals = ApprovalService(db)

    async def raise_audit(self, data: AuditCreate) -> AuditResponse:
        approval = await self.approvals.create(
            ApprovalCreate(entity_type=data.entity_type, entity_id=data.entity_id)
        )
        return await self._to_response(approval)

    async def get(self, audit_id: int) -> AuditResponse:
        approval = await self.approvals.get(audit_id)
        return await self._to_response(approval)

    async def get_all(self) -> list[AuditResponse]:
        approvals = await self.approvals.get_all()
        return [await self._to_response(a) for a in approvals]

    async def get_by_entity(self, entity_type: str, entity_id: int) -> list[AuditResponse]:
        approvals = await self.approvals.get_by_entity(entity_type, entity_id)
        return [await self._to_response(a) for a in approvals]

    async def events(self, audit_id: int) -> list[ApprovalEvent]:
        return await self.approvals.get_events(audit_id)

    async def submit(self, audit_id: int, data: AuditSubmit) -> AuditResponse:
        comment = format_submission_comment(data.audit_type, data.notes)
        approval = await self.approvals.submit(
            audit_id, ApprovalTransition(actor=data.auditor, comment=comment)
        )
        return await self._to_response(approval)

    async def review(self, audit_id: int, data: ApprovalTransition) -> AuditResponse:
        approval = await self.approvals.review(audit_id, data)
        return await self._to_response(approval)

    async def approve(self, audit_id: int, data: ApprovalTransition) -> AuditResponse:
        approval = await self.approvals.approve(audit_id, data)
        return await self._to_response(approval)

    async def reject(self, audit_id: int, data: ApprovalTransition) -> AuditResponse:
        if not data.comment or not data.comment.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A rejected audit must include a reason",
            )
        approval = await self.approvals.reject(audit_id, data)
        return await self._to_response(approval)

    async def close(self, audit_id: int, data: ApprovalTransition) -> AuditResponse:
        approval = await self.approvals.close(audit_id, data)
        return await self._to_response(approval)

    async def _to_response(self, approval: Approval) -> AuditResponse:
        events = await self.approvals.get_events(approval.id)
        submitted_events = [e for e in events if e.to_status == ApprovalStatus.SUBMITTED]
        parsed = parse_submission_comment(
            submitted_events[-1].comment if submitted_events else None
        )
        return AuditResponse(
            id=approval.id,
            entity_type=approval.entity_type,
            entity_id=approval.entity_id,
            status=approval.status,
            current_assignee=approval.current_assignee,
            created_at=approval.created_at,
            updated_at=approval.updated_at,
            audit_type=parsed.audit_type,
            notes=parsed.notes,
        )
