from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ChecklistInstanceStatus, ChecklistItemState
from app.models.checklist_instance import ChecklistInstance
from app.models.checklist_instance_item import ChecklistInstanceItem
from app.models.checklist_template import ChecklistTemplate
from app.models.checklist_template_item import ChecklistTemplateItem
from app.repositories.checklist_instance_item_repository import ChecklistInstanceItemRepository
from app.repositories.checklist_instance_repository import ChecklistInstanceRepository
from app.repositories.checklist_template_item_repository import ChecklistTemplateItemRepository
from app.repositories.checklist_template_repository import ChecklistTemplateRepository
from app.schemas.checklist_instance import ChecklistInstanceCreate
from app.schemas.checklist_instance_item import ChecklistInstanceItemComplete
from app.schemas.checklist_template import ChecklistTemplateCreate, ChecklistTemplateUpdate
from app.schemas.checklist_template_item import ChecklistTemplateItemCreate


class ChecklistService:
    def __init__(self, db: AsyncSession):
        self.template_repo = ChecklistTemplateRepository(db)
        self.template_item_repo = ChecklistTemplateItemRepository(db)
        self.instance_repo = ChecklistInstanceRepository(db)
        self.instance_item_repo = ChecklistInstanceItemRepository(db)

    # -- templates --------------------------------------------------------

    async def create_template(self, data: ChecklistTemplateCreate) -> ChecklistTemplate:
        template = ChecklistTemplate(
            name=data.name,
            description=data.description,
            items=[
                ChecklistTemplateItem(**item.model_dump()) for item in data.items
            ],
        )
        return await self.template_repo.create(template)

    async def get_template(self, template_id: int) -> ChecklistTemplate:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return template

    async def get_all_templates(self) -> list[ChecklistTemplate]:
        return await self.template_repo.get_all()

    async def update_template(
        self, template_id: int, data: ChecklistTemplateUpdate
    ) -> ChecklistTemplate:
        template = await self.get_template(template_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.template_repo.update(template, update_data)

    async def delete_template(self, template_id: int) -> None:
        template = await self.get_template(template_id)
        await self.template_repo.delete(template)

    async def add_template_item(
        self, template_id: int, data: ChecklistTemplateItemCreate
    ) -> ChecklistTemplateItem:
        await self.get_template(template_id)
        item = ChecklistTemplateItem(template_id=template_id, **data.model_dump())
        return await self.template_item_repo.create(item)

    async def delete_template_item(self, template_id: int, item_id: int) -> None:
        item = await self.template_item_repo.get_by_id(item_id)
        if not item or item.template_id != template_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        await self.template_item_repo.delete(item)

    # -- instances ----------------------------------------------------------

    async def create_instance(self, data: ChecklistInstanceCreate) -> ChecklistInstance:
        template = await self.get_template(data.template_id)
        instance = ChecklistInstance(
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            template_id=template.id,
            status=ChecklistInstanceStatus.NOT_STARTED,
            items=[
                ChecklistInstanceItem(
                    template_item_id=template_item.id,
                    label=template_item.label,
                    sequence=template_item.sequence,
                    is_required=template_item.is_required,
                    requires_evidence=template_item.requires_evidence,
                )
                for template_item in template.items
            ],
        )
        return await self.instance_repo.create(instance)

    async def get_instance(self, instance_id: int) -> ChecklistInstance:
        instance = await self.instance_repo.get_by_id(instance_id)
        if not instance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
        return instance

    async def get_all_instances(self) -> list[ChecklistInstance]:
        return await self.instance_repo.get_all()

    async def get_instances_by_entity(
        self, entity_type: str, entity_id: int
    ) -> list[ChecklistInstance]:
        return await self.instance_repo.get_by_entity(entity_type, entity_id)

    async def delete_instance(self, instance_id: int) -> None:
        instance = await self.get_instance(instance_id)
        await self.instance_repo.delete(instance)

    async def complete_item(
        self, instance_id: int, item_id: int, data: ChecklistInstanceItemComplete
    ) -> ChecklistInstance:
        instance = await self.get_instance(instance_id)
        item = next((i for i in instance.items if i.id == item_id), None)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        update_data = data.model_dump(exclude_unset=True)
        update_data["completed_at"] = datetime.now(UTC)
        await self.instance_item_repo.update(item, update_data)

        return await self._sync_instance_status(instance_id)

    async def _sync_instance_status(self, instance_id: int) -> ChecklistInstance:
        instance = await self.get_instance(instance_id)
        states = [item.state for item in instance.items]
        if states and all(state != ChecklistItemState.PENDING for state in states):
            new_status = ChecklistInstanceStatus.COMPLETED
        elif any(state != ChecklistItemState.PENDING for state in states):
            new_status = ChecklistInstanceStatus.IN_PROGRESS
        else:
            new_status = ChecklistInstanceStatus.NOT_STARTED
        return await self.instance_repo.update(instance, {"status": new_status})
