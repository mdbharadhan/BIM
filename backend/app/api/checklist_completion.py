from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.checklist_completion import ChecklistCompletionStatus
from app.services.checklist_completion_service import ChecklistCompletionService

router = APIRouter(tags=["Checklists"])


@router.get(
    "/checklist-instances/{instance_id}/completion",
    response_model=ChecklistCompletionStatus,
)
async def get_checklist_completion(
    instance_id: int, db: AsyncSession = Depends(get_db)
) -> ChecklistCompletionStatus:
    return await ChecklistCompletionService(db).get_completion(instance_id)
