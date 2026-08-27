from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.checklist_completion import ItemSnapshot, summarize
from app.schemas.checklist_completion import ChecklistCompletionStatus
from app.services.checklist_service import ChecklistService


class ChecklistCompletionService:
    def __init__(self, db: AsyncSession):
        self.checklists = ChecklistService(db)

    async def get_completion(self, instance_id: int) -> ChecklistCompletionStatus:
        instance = await self.checklists.get_instance(instance_id)
        snapshots = [
            ItemSnapshot(label=item.label, state=item.state, is_required=item.is_required)
            for item in instance.items
        ]
        summary = summarize(snapshots)
        return ChecklistCompletionStatus(instance_id=instance.id, **asdict(summary))
