from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.checklist_template import ChecklistTemplate


class ChecklistTemplateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, template: ChecklistTemplate) -> ChecklistTemplate:
        self.db.add(template)
        await self.db.commit()
        # Re-fetch with items eager-loaded: session.refresh() would expire and
        # then lazy-load the relationship, which fails outside an async context.
        refreshed = await self.get_by_id(template.id)
        if refreshed is None:
            raise RuntimeError(f"Template {template.id} vanished immediately after write")
        return refreshed

    async def get_by_id(self, template_id: int) -> ChecklistTemplate | None:
        result = await self.db.execute(
            select(ChecklistTemplate)
            .options(selectinload(ChecklistTemplate.items))
            .where(ChecklistTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ChecklistTemplate]:
        result = await self.db.execute(
            select(ChecklistTemplate).options(selectinload(ChecklistTemplate.items))
        )
        return list(result.scalars().all())

    async def update(self, template: ChecklistTemplate, data: dict) -> ChecklistTemplate:
        for key, value in data.items():
            setattr(template, key, value)
        await self.db.commit()
        refreshed = await self.get_by_id(template.id)
        if refreshed is None:
            raise RuntimeError(f"Template {template.id} vanished immediately after write")
        return refreshed

    async def delete(self, template: ChecklistTemplate) -> None:
        await self.db.delete(template)
        await self.db.commit()
