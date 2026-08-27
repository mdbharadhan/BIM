import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.design_review import DesignReviewType
from app.schemas.approval import ApprovalTransition
from app.schemas.design_review import DesignReviewCreate, DesignReviewSubmit
from app.services.design_review_service import DesignReviewService


async def _raised(service: DesignReviewService):
    return await service.raise_review(DesignReviewCreate(entity_type="document", entity_id=1))


async def test_raise_review_defaults_to_draft_with_no_review_type(db_session: AsyncSession):
    service = DesignReviewService(db_session)
    review = await _raised(service)
    assert review.status == "draft"
    assert review.review_type is None
    assert review.entity_type == "document"


async def test_submit_records_review_type_and_notes(db_session: AsyncSession):
    service = DesignReviewService(db_session)
    review = await _raised(service)

    submitted = await service.submit(
        review.id,
        DesignReviewSubmit(
            review_type=DesignReviewType.SPEC_REVIEW,
            reviewer="lead-engineer@example.com",
            notes="spec matches drawing rev C",
        ),
    )
    assert submitted.status == "submitted"
    assert submitted.review_type is DesignReviewType.SPEC_REVIEW
    assert submitted.notes == "spec matches drawing rev C"


async def test_get_reflects_the_latest_submission(db_session: AsyncSession):
    """Resubmission after rejection should update the reported review_type."""
    service = DesignReviewService(db_session)
    review = await _raised(service)
    await service.submit(review.id, DesignReviewSubmit(review_type=DesignReviewType.PEER_REVIEW))
    await service.review(review.id, ApprovalTransition(actor="reviewer@example.com"))
    await service.reject(
        review.id, ApprovalTransition(actor="reviewer@example.com", comment="needs rework")
    )
    await service.submit(
        review.id, DesignReviewSubmit(review_type=DesignReviewType.DESIGN_CHANGE, notes="revised")
    )

    current = await service.get(review.id)
    assert current.review_type is DesignReviewType.DESIGN_CHANGE
    assert current.notes == "revised"


async def test_reject_without_comment_is_rejected(db_session: AsyncSession):
    service = DesignReviewService(db_session)
    review = await _raised(service)
    await service.submit(review.id, DesignReviewSubmit(review_type=DesignReviewType.DESIGN_REVIEW))
    await service.review(review.id, ApprovalTransition(actor="reviewer@example.com"))

    with pytest.raises(HTTPException) as exc_info:
        await service.reject(review.id, ApprovalTransition(actor="reviewer@example.com"))
    assert exc_info.value.status_code == 400


async def test_full_design_review_lifecycle(db_session: AsyncSession):
    service = DesignReviewService(db_session)
    review = await _raised(service)

    await service.submit(
        review.id,
        DesignReviewSubmit(
            review_type=DesignReviewType.INDEPENDENT_DESIGN_CHECK, reviewer="qa@example.com"
        ),
    )
    await service.review(review.id, ApprovalTransition(actor="reviewer@example.com"))
    approved = await service.approve(review.id, ApprovalTransition(actor="reviewer@example.com"))
    assert approved.status == "approved"
    assert approved.review_type is DesignReviewType.INDEPENDENT_DESIGN_CHECK

    closed = await service.close(review.id, ApprovalTransition(actor="qa@example.com"))
    assert closed.status == "closed"

    events = await service.events(review.id)
    assert [e.to_status for e in events] == [
        "draft",
        "submitted",
        "under_review",
        "approved",
        "closed",
    ]
