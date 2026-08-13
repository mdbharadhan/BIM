from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval_event import ApprovalEvent


class ApprovalEventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, event: ApprovalEvent) -> ApprovalEvent:
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_by_approval(self, approval_id: int) -> list[ApprovalEvent]:
        result = await self.db.execute(
            select(ApprovalEvent)
            .where(ApprovalEvent.approval_id == approval_id)
            .order_by(ApprovalEvent.created_at)
        )
        return list(result.scalars().all())
