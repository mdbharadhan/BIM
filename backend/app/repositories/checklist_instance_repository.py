from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.checklist_instance import ChecklistInstance


class ChecklistInstanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, instance: ChecklistInstance) -> ChecklistInstance:
        self.db.add(instance)
        await self.db.commit()
        refreshed = await self.get_by_id(instance.id)
        if refreshed is None:
            raise RuntimeError(f"Instance {instance.id} vanished immediately after write")
        return refreshed

    async def get_by_id(self, instance_id: int) -> ChecklistInstance | None:
        result = await self.db.execute(
            select(ChecklistInstance)
            .options(selectinload(ChecklistInstance.items))
            .where(ChecklistInstance.id == instance_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ChecklistInstance]:
        result = await self.db.execute(
            select(ChecklistInstance).options(selectinload(ChecklistInstance.items))
        )
        return list(result.scalars().all())

    async def get_by_entity(self, entity_type: str, entity_id: int) -> list[ChecklistInstance]:
        result = await self.db.execute(
            select(ChecklistInstance)
            .options(selectinload(ChecklistInstance.items))
            .where(
                ChecklistInstance.entity_type == entity_type,
                ChecklistInstance.entity_id == entity_id,
            )
        )
        return list(result.scalars().all())

    async def update(self, instance: ChecklistInstance, data: dict) -> ChecklistInstance:
        for key, value in data.items():
            setattr(instance, key, value)
        await self.db.commit()
        refreshed = await self.get_by_id(instance.id)
        if refreshed is None:
            raise RuntimeError(f"Instance {instance.id} vanished immediately after write")
        return refreshed

    async def delete(self, instance: ChecklistInstance) -> None:
        await self.db.delete(instance)
        await self.db.commit()
