from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval


class ApprovalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, approval: Approval) -> Approval:
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def get_by_id(self, approval_id: int) -> Approval | None:
        result = await self.db.execute(select(Approval).where(Approval.id == approval_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Approval]:
        result = await self.db.execute(select(Approval))
        return list(result.scalars().all())

    async def get_by_entity(self, entity_type: str, entity_id: int) -> list[Approval]:
        result = await self.db.execute(
            select(Approval).where(
                Approval.entity_type == entity_type, Approval.entity_id == entity_id
            )
        )
        return list(result.scalars().all())

    async def update(self, approval: Approval, data: dict) -> Approval:
        for key, value in data.items():
            setattr(approval, key, value)
        await self.db.commit()
        await self.db.refresh(approval)
        return approval
