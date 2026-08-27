"""Design QA review/approval workflow — a thin layer over the Approval
primitive's state machine, not a new primitive.

Covers design reviews, peer review, spec review, constructability review,
value engineering, independent design check, and design change management —
the review/approval half of Design QA. The BIM-coordination/clash-resolution
half depends on the BIM-Vision subsystem and is explicitly out of scope here.

A design review is typically raised against entity_type="document" (a real
primitive table — see docs/primitives/approval.md's Design QA example use),
so unlike NCR/Audit it doesn't need the Room-stand-in pattern. review_type
has no home on the Approval row itself (see app.domain.design_review's module
docstring), so it travels inside the submit transition's comment and is
parsed back out of the event history for display, same convention as Audit.
As with NCR and Audit, a rejection must include a reason.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.design_review import format_submission_comment, parse_submission_comment
from app.domain.enums import ApprovalStatus
from app.models.approval import Approval
from app.models.approval_event import ApprovalEvent
from app.schemas.approval import ApprovalCreate, ApprovalTransition
from app.schemas.design_review import DesignReviewCreate, DesignReviewResponse, DesignReviewSubmit
from app.services.approval_service import ApprovalService


class DesignReviewService:
    def __init__(self, db: AsyncSession):
        self.approvals = ApprovalService(db)

    async def raise_review(self, data: DesignReviewCreate) -> DesignReviewResponse:
        approval = await self.approvals.create(
            ApprovalCreate(entity_type=data.entity_type, entity_id=data.entity_id)
        )
        return await self._to_response(approval)

    async def get(self, review_id: int) -> DesignReviewResponse:
        approval = await self.approvals.get(review_id)
        return await self._to_response(approval)

    async def get_all(self) -> list[DesignReviewResponse]:
        approvals = await self.approvals.get_all()
        return [await self._to_response(a) for a in approvals]

    async def get_by_entity(self, entity_type: str, entity_id: int) -> list[DesignReviewResponse]:
        approvals = await self.approvals.get_by_entity(entity_type, entity_id)
        return [await self._to_response(a) for a in approvals]

    async def events(self, review_id: int) -> list[ApprovalEvent]:
        return await self.approvals.get_events(review_id)

    async def submit(self, review_id: int, data: DesignReviewSubmit) -> DesignReviewResponse:
        comment = format_submission_comment(data.review_type, data.notes)
        approval = await self.approvals.submit(
            review_id, ApprovalTransition(actor=data.reviewer, comment=comment)
        )
        return await self._to_response(approval)

    async def review(self, review_id: int, data: ApprovalTransition) -> DesignReviewResponse:
        approval = await self.approvals.review(review_id, data)
        return await self._to_response(approval)

    async def approve(self, review_id: int, data: ApprovalTransition) -> DesignReviewResponse:
        approval = await self.approvals.approve(review_id, data)
        return await self._to_response(approval)

    async def reject(self, review_id: int, data: ApprovalTransition) -> DesignReviewResponse:
        if not data.comment or not data.comment.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A rejected design review must include a reason",
            )
        approval = await self.approvals.reject(review_id, data)
        return await self._to_response(approval)

    async def close(self, review_id: int, data: ApprovalTransition) -> DesignReviewResponse:
        approval = await self.approvals.close(review_id, data)
        return await self._to_response(approval)

    async def _to_response(self, approval: Approval) -> DesignReviewResponse:
        events = await self.approvals.get_events(approval.id)
        submitted_events = [e for e in events if e.to_status == ApprovalStatus.SUBMITTED]
        parsed = parse_submission_comment(
            submitted_events[-1].comment if submitted_events else None
        )
        return DesignReviewResponse(
            id=approval.id,
            entity_type=approval.entity_type,
            entity_id=approval.entity_id,
            status=approval.status,
            current_assignee=approval.current_assignee,
            created_at=approval.created_at,
            updated_at=approval.updated_at,
            review_type=parsed.review_type,
            notes=parsed.notes,
        )
