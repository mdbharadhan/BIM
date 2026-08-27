from app.repositories.checklist_template_repository import ChecklistTemplateRepository
from app.seeds.checklist import (
    ALL_TEMPLATES,
    CONCRETE_POUR_INSPECTION,
    MATERIAL_DELIVERY_INSPECTION,
    seed_all,
    seed_template,
)


async def test_seed_creates_template_and_items(db_session):
    template = await seed_template(db_session, CONCRETE_POUR_INSPECTION)

    assert template.name == CONCRETE_POUR_INSPECTION.name
    assert len(template.items) == len(CONCRETE_POUR_INSPECTION.items)
    assert {item.label for item in template.items} == {
        item.label for item in CONCRETE_POUR_INSPECTION.items
    }


async def test_seed_is_idempotent(db_session):
    await seed_all(db_session)
    await seed_all(db_session)

    templates = await ChecklistTemplateRepository(db_session).get_all()
    assert len(templates) == len(ALL_TEMPLATES)

    pour = next(t for t in templates if t.name == CONCRETE_POUR_INSPECTION.name)
    assert len(pour.items) == len(CONCRETE_POUR_INSPECTION.items)


async def test_rerun_updates_changed_description(db_session):
    template = await seed_template(db_session, CONCRETE_POUR_INSPECTION)
    repo = ChecklistTemplateRepository(db_session)
    await repo.update(template, {"description": "stale description"})

    reseeded = await seed_template(db_session, CONCRETE_POUR_INSPECTION)

    assert reseeded.description == CONCRETE_POUR_INSPECTION.description


async def test_rerun_does_not_duplicate_items(db_session):
    await seed_template(db_session, CONCRETE_POUR_INSPECTION)
    template = await seed_template(db_session, CONCRETE_POUR_INSPECTION)

    assert len(template.items) == len(CONCRETE_POUR_INSPECTION.items)


async def test_material_delivery_template_matches_material_delivery_scenario(db_session):
    """Same sand-delivery scenario the IS 383 compliance seed evaluates."""
    template = await seed_template(db_session, MATERIAL_DELIVERY_INSPECTION)

    labels = {item.label for item in template.items}
    assert "Material Test Certificate on file" in labels
    assert "Source approval confirmed" in labels
