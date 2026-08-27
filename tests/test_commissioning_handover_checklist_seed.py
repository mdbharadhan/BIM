from app.repositories.checklist_template_repository import ChecklistTemplateRepository
from app.seeds.checklist import (
    ALL_TEMPLATES,
    FINAL_HANDOVER_CHECKLIST,
    PRE_COMMISSIONING_CHECKLIST,
    seed_all,
    seed_template,
)

NEW_TEMPLATES = [PRE_COMMISSIONING_CHECKLIST, FINAL_HANDOVER_CHECKLIST]


async def test_each_new_template_seeds_its_items(db_session):
    for seed in NEW_TEMPLATES:
        template = await seed_template(db_session, seed)
        assert template.name == seed.name
        assert len(template.items) == len(seed.items)
        assert {item.label for item in template.items} == {i.label for i in seed.items}


async def test_seed_all_includes_the_new_templates(db_session):
    await seed_all(db_session)

    templates = await ChecklistTemplateRepository(db_session).get_all()
    names = {t.name for t in templates}
    assert len(templates) == len(ALL_TEMPLATES)
    for seed in NEW_TEMPLATES:
        assert seed.name in names


async def test_rerun_does_not_duplicate_items(db_session):
    await seed_template(db_session, PRE_COMMISSIONING_CHECKLIST)
    template = await seed_template(db_session, PRE_COMMISSIONING_CHECKLIST)

    assert len(template.items) == len(PRE_COMMISSIONING_CHECKLIST.items)


async def test_handover_checklist_covers_documentation_and_acceptance():
    """Guards the scope the phase asked for: punch list, as-built documents,
    O&M manuals, warranty documents, client acceptance."""
    labels = " ".join(i.label.lower() for i in FINAL_HANDOVER_CHECKLIST.items)
    for term in ("punch list", "as-built", "o&m manual", "warranty", "acceptance"):
        assert term in labels


async def test_item_sequences_are_unique_and_start_at_zero_within_each_template():
    for seed in NEW_TEMPLATES:
        sequences = sorted(i.sequence for i in seed.items)
        assert sequences == list(range(len(seed.items))), seed.name
