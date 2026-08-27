from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.approval_event import ApprovalEvent
from app.schemas.approval import ApprovalTransition
from app.schemas.design_review import (
    DesignReviewCreate,
    DesignReviewEventResponse,
    DesignReviewResponse,
    DesignReviewSubmit,
)
from app.services.design_review_service import DesignReviewService

router = APIRouter(tags=["Design Reviews"])


@router.post("/design-reviews", response_model=DesignReviewResponse, status_code=201)
async def raise_design_review(
    data: DesignReviewCreate, db: AsyncSession = Depends(get_db)
) -> DesignReviewResponse:
    return await DesignReviewService(db).raise_review(data)


@router.get("/design-reviews", response_model=list[DesignReviewResponse])
async def list_design_reviews(db: AsyncSession = Depends(get_db)) -> list[DesignReviewResponse]:
    return await DesignReviewService(db).get_all()


@router.get("/design-reviews/{review_id}", response_model=DesignReviewResponse)
async def get_design_review(
    review_id: int, db: AsyncSession = Depends(get_db)
) -> DesignReviewResponse:
    return await DesignReviewService(db).get(review_id)


@router.get("/design-reviews/{review_id}/events", response_model=list[DesignReviewEventResponse])
async def list_design_review_events(
    review_id: int, db: AsyncSession = Depends(get_db)
) -> list[ApprovalEvent]:
    return await DesignReviewService(db).events(review_id)


@router.post("/design-reviews/{review_id}/submit", response_model=DesignReviewResponse)
async def submit_design_review(
    review_id: int, data: DesignReviewSubmit, db: AsyncSession = Depends(get_db)
) -> DesignReviewResponse:
    return await DesignReviewService(db).submit(review_id, data)


@router.post("/design-reviews/{review_id}/review", response_model=DesignReviewResponse)
async def review_design_review(
    review_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> DesignReviewResponse:
    return await DesignReviewService(db).review(review_id, data)


@router.post("/design-reviews/{review_id}/approve", response_model=DesignReviewResponse)
async def approve_design_review(
    review_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> DesignReviewResponse:
    return await DesignReviewService(db).approve(review_id, data)


@router.post("/design-reviews/{review_id}/reject", response_model=DesignReviewResponse)
async def reject_design_review(
    review_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> DesignReviewResponse:
    return await DesignReviewService(db).reject(review_id, data)


@router.post("/design-reviews/{review_id}/close", response_model=DesignReviewResponse)
async def close_design_review(
    review_id: int, data: ApprovalTransition, db: AsyncSession = Depends(get_db)
) -> DesignReviewResponse:
    return await DesignReviewService(db).close(review_id, data)


@router.get(
    "/entities/{entity_type}/{entity_id}/design-reviews",
    response_model=list[DesignReviewResponse],
)
async def get_design_reviews_by_entity(
    entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db)
) -> list[DesignReviewResponse]:
    return await DesignReviewService(db).get_by_entity(entity_type, entity_id)
