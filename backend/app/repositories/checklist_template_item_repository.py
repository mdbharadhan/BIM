from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.checklist_template_item import ChecklistTemplateItem


class ChecklistTemplateItemRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, item: ChecklistTemplateItem) -> ChecklistTemplateItem:
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_by_id(self, item_id: int) -> ChecklistTemplateItem | None:
        result = await self.db.execute(
            select(ChecklistTemplateItem).where(ChecklistTemplateItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, item: ChecklistTemplateItem) -> None:
        await self.db.delete(item)
        await self.db.commit()
