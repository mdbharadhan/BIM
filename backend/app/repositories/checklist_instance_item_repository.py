from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checklist_instance_item import ChecklistInstanceItem


class ChecklistInstanceItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, item_id: int) -> ChecklistInstanceItem | None:
        result = await self.db.execute(
            select(ChecklistInstanceItem).where(ChecklistInstanceItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def update(self, item: ChecklistInstanceItem, data: dict) -> ChecklistInstanceItem:
        for key, value in data.items():
            setattr(item, key, value)
        await self.db.commit()
        await self.db.refresh(item)
        return item
