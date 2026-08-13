import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ChecklistInstanceStatus, ChecklistItemState
from app.schemas.checklist_instance import ChecklistInstanceCreate
from app.schemas.checklist_instance_item import ChecklistInstanceItemComplete
from app.schemas.checklist_template import ChecklistTemplateCreate
from app.schemas.checklist_template_item import ChecklistTemplateItemCreate
from app.services.checklist_service import ChecklistService


async def _make_template(service: ChecklistService):
    return await service.create_template(
        ChecklistTemplateCreate(
            name="Pour Checklist",
            items=[
                ChecklistTemplateItemCreate(label="Formwork inspected"),
                ChecklistTemplateItemCreate(label="Rebar cover verified"),
            ],
        )
    )


async def test_create_instance_snapshots_template_items(db_session: AsyncSession):
    service = ChecklistService(db_session)
    template = await _make_template(service)

    instance = await service.create_instance(
        ChecklistInstanceCreate(template_id=template.id, entity_type="room", entity_id=1)
    )

    assert len(instance.items) == 2
    assert {item.label for item in instance.items} == {
        "Formwork inspected",
        "Rebar cover verified",
    }
    assert instance.status == ChecklistInstanceStatus.NOT_STARTED


async def test_complete_all_items_marks_instance_completed(db_session: AsyncSession):
    service = ChecklistService(db_session)
    template = await _make_template(service)
    instance = await service.create_instance(
        ChecklistInstanceCreate(template_id=template.id, entity_type="room", entity_id=1)
    )

    for item in instance.items:
        instance = await service.complete_item(
            instance.id, item.id, ChecklistInstanceItemComplete(state=ChecklistItemState.PASS_)
        )

    assert instance.status == ChecklistInstanceStatus.COMPLETED


async def test_create_instance_with_bogus_template_raises_404(db_session: AsyncSession):
    service = ChecklistService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_instance(
            ChecklistInstanceCreate(template_id=999, entity_type="room", entity_id=1)
        )
    assert exc_info.value.status_code == 404
