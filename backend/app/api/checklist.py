from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.checklist_instance import ChecklistInstance
from app.models.checklist_template import ChecklistTemplate
from app.models.checklist_template_item import ChecklistTemplateItem
from app.schemas.checklist_instance import ChecklistInstanceCreate, ChecklistInstanceResponse
from app.schemas.checklist_instance_item import ChecklistInstanceItemComplete
from app.schemas.checklist_template import (
    ChecklistTemplateCreate,
    ChecklistTemplateResponse,
    ChecklistTemplateUpdate,
)
from app.schemas.checklist_template_item import (
    ChecklistTemplateItemCreate,
    ChecklistTemplateItemResponse,
)
from app.services.checklist_service import ChecklistService

router = APIRouter(tags=["Checklists"])


@router.post("/checklist-templates", response_model=ChecklistTemplateResponse, status_code=201)
async def create_template(
    data: ChecklistTemplateCreate, db: AsyncSession = Depends(get_db)
) -> ChecklistTemplate:
    return await ChecklistService(db).create_template(data)


@router.get("/checklist-templates", response_model=list[ChecklistTemplateResponse])
async def list_templates(db: AsyncSession = Depends(get_db)) -> list[ChecklistTemplate]:
    return await ChecklistService(db).get_all_templates()


@router.get("/checklist-templates/{template_id}", response_model=ChecklistTemplateResponse)
async def get_template(template_id: int, db: AsyncSession = Depends(get_db)) -> ChecklistTemplate:
    return await ChecklistService(db).get_template(template_id)


@router.put("/checklist-templates/{template_id}", response_model=ChecklistTemplateResponse)
async def update_template(
    template_id: int, data: ChecklistTemplateUpdate, db: AsyncSession = Depends(get_db)
) -> ChecklistTemplate:
    return await ChecklistService(db).update_template(template_id, data)


@router.delete("/checklist-templates/{template_id}", status_code=204)
async def delete_template(template_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await ChecklistService(db).delete_template(template_id)


@router.post(
    "/checklist-templates/{template_id}/items",
    response_model=ChecklistTemplateItemResponse,
    status_code=201,
)
async def add_template_item(
    template_id: int, data: ChecklistTemplateItemCreate, db: AsyncSession = Depends(get_db)
) -> ChecklistTemplateItem:
    return await ChecklistService(db).add_template_item(template_id, data)


@router.delete("/checklist-templates/{template_id}/items/{item_id}", status_code=204)
async def delete_template_item(
    template_id: int, item_id: int, db: AsyncSession = Depends(get_db)
) -> None:
    await ChecklistService(db).delete_template_item(template_id, item_id)


@router.post("/checklist-instances", response_model=ChecklistInstanceResponse, status_code=201)
async def create_instance(
    data: ChecklistInstanceCreate, db: AsyncSession = Depends(get_db)
) -> ChecklistInstance:
    return await ChecklistService(db).create_instance(data)


@router.get("/checklist-instances", response_model=list[ChecklistInstanceResponse])
async def list_instances(db: AsyncSession = Depends(get_db)) -> list[ChecklistInstance]:
    return await ChecklistService(db).get_all_instances()


@router.get("/checklist-instances/{instance_id}", response_model=ChecklistInstanceResponse)
async def get_instance(instance_id: int, db: AsyncSession = Depends(get_db)) -> ChecklistInstance:
    return await ChecklistService(db).get_instance(instance_id)


@router.delete("/checklist-instances/{instance_id}", status_code=204)
async def delete_instance(instance_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await ChecklistService(db).delete_instance(instance_id)


@router.patch(
    "/checklist-instances/{instance_id}/items/{item_id}",
    response_model=ChecklistInstanceResponse,
)
async def complete_instance_item(
    instance_id: int,
    item_id: int,
    data: ChecklistInstanceItemComplete,
    db: AsyncSession = Depends(get_db),
) -> ChecklistInstance:
    return await ChecklistService(db).complete_item(instance_id, item_id, data)


@router.get(
    "/entities/{entity_type}/{entity_id}/checklist-instances",
    response_model=list[ChecklistInstanceResponse],
)
async def get_instances_by_entity(
    entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db)
) -> list[ChecklistInstance]:
    return await ChecklistService(db).get_instances_by_entity(entity_type, entity_id)
