"""Seed real checklist templates.

Idempotent: safe to re-run. Templates are matched on `name` (create if
missing, else update description in place). Items are matched on `label`
within a template and only ever added, never rewritten — ChecklistService
exposes `add_template_item`/`delete_template_item` but no update, so
correcting a seeded item's fields today means editing this file and manually
deleting the stale item first; see the template docstring below for detail.

    python -m app.seeds.checklist          # run from backend/
"""

import asyncio
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal, Base, engine
from app.models.checklist_template import ChecklistTemplate
from app.schemas.checklist_template import ChecklistTemplateCreate, ChecklistTemplateUpdate
from app.schemas.checklist_template_item import ChecklistTemplateItemCreate
from app.services.checklist_service import ChecklistService


@dataclass(frozen=True)
class ItemSeed:
    label: str
    sequence: int
    is_required: bool = True
    requires_evidence: bool = False


@dataclass(frozen=True)
class TemplateSeed:
    name: str
    description: str | None
    items: list[ItemSeed] = field(default_factory=list)


CONCRETE_POUR_INSPECTION = TemplateSeed(
    name="Concrete Pour Inspection",
    description=(
        "Pre-pour and pour-stage verification for a structural concrete pour, from "
        "formwork through curing sign-off."
    ),
    items=[
        ItemSeed(label="Formwork inspected and approved", sequence=0, requires_evidence=True),
        ItemSeed(label="Rebar cover verified against drawing", sequence=1, requires_evidence=True),
        ItemSeed(label="Pour sequence and method confirmed", sequence=2),
        ItemSeed(label="Curing method and duration recorded", sequence=3, requires_evidence=True),
    ],
)

# Same sand-delivery scenario the IS 383 compliance seed evaluates — this
# checklist is the inspection step; compliance-evaluations records the
# measured values against IS 383 once this passes.
MATERIAL_DELIVERY_INSPECTION = TemplateSeed(
    name="Material Delivery Inspection",
    description=(
        "Receiving inspection for a material delivery (e.g. a sand load): visual "
        "condition, paperwork, and source traceability before it enters compliance testing."
    ),
    items=[
        ItemSeed(label="Visual inspection of delivery passed", sequence=0, requires_evidence=True),
        ItemSeed(label="Material Test Certificate on file", sequence=1),
        ItemSeed(label="Source approval confirmed", sequence=2),
    ],
)

# Precedes FINAL_HANDOVER_CHECKLIST in a building's lifecycle: this verifies a
# system or building is ready to go live; handover verifies it's ready to
# leave the contractor's hands.
PRE_COMMISSIONING_CHECKLIST = TemplateSeed(
    name="Pre-Commissioning Checklist",
    description=(
        "Readiness verification before a system or building goes live: installation "
        "complete, functional tests passed, safety systems verified, and documentation "
        "current."
    ),
    items=[
        ItemSeed(label="Installation complete per approved drawings", sequence=0),
        ItemSeed(
            label="Functional performance tests completed", sequence=1, requires_evidence=True
        ),
        ItemSeed(
            label="Safety systems tested (fire alarm, emergency lighting, egress)",
            sequence=2,
            requires_evidence=True,
        ),
        ItemSeed(label="Punch list items closed out", sequence=3),
        ItemSeed(label="Equipment tagged and labeled", sequence=4),
        ItemSeed(
            label="As-built drawings updated to reflect installed condition",
            sequence=5,
            requires_evidence=True,
        ),
        ItemSeed(
            label="Commissioning authority sign-off obtained", sequence=6, requires_evidence=True
        ),
    ],
)

FINAL_HANDOVER_CHECKLIST = TemplateSeed(
    name="Final Handover Checklist",
    description=(
        "Client handover readiness: outstanding defects closed, documentation and "
        "training delivered, and formal acceptance obtained."
    ),
    items=[
        ItemSeed(label="Punch list / snag list fully closed", sequence=0),
        ItemSeed(label="As-built documents submitted", sequence=1, requires_evidence=True),
        ItemSeed(label="O&M manuals submitted", sequence=2, requires_evidence=True),
        ItemSeed(label="Warranty documents submitted", sequence=3, requires_evidence=True),
        ItemSeed(label="Client O&M staff training completed", sequence=4, requires_evidence=True),
        ItemSeed(label="Spare parts and tools handed over", sequence=5),
        ItemSeed(label="Keys and access credentials transferred", sequence=6),
        ItemSeed(label="Client acceptance sign-off obtained", sequence=7, requires_evidence=True),
    ],
)

ALL_TEMPLATES: list[TemplateSeed] = [
    CONCRETE_POUR_INSPECTION,
    MATERIAL_DELIVERY_INSPECTION,
    PRE_COMMISSIONING_CHECKLIST,
    FINAL_HANDOVER_CHECKLIST,
]


async def seed_template(db: AsyncSession, seed: TemplateSeed) -> ChecklistTemplate:
    """Upsert one template and add any of its seeded items not already present.

    Returns the persisted template.
    """
    service = ChecklistService(db)
    templates = await service.get_all_templates()
    existing = next((t for t in templates if t.name == seed.name), None)

    if existing is None:
        template = await service.create_template(
            ChecklistTemplateCreate(
                name=seed.name,
                description=seed.description,
                items=[
                    ChecklistTemplateItemCreate(
                        label=item.label,
                        sequence=item.sequence,
                        is_required=item.is_required,
                        requires_evidence=item.requires_evidence,
                    )
                    for item in seed.items
                ],
            )
        )
    elif existing.description != seed.description:
        template = await service.update_template(
            existing.id, ChecklistTemplateUpdate(description=seed.description)
        )
    else:
        template = existing

    present_labels = {item.label for item in template.items}
    for item_seed in seed.items:
        if item_seed.label not in present_labels:
            await service.add_template_item(
                template.id,
                ChecklistTemplateItemCreate(
                    label=item_seed.label,
                    sequence=item_seed.sequence,
                    is_required=item_seed.is_required,
                    requires_evidence=item_seed.requires_evidence,
                ),
            )

    return await service.get_template(template.id)


async def seed_all(db: AsyncSession) -> None:
    for seed in ALL_TEMPLATES:
        template = await seed_template(db, seed)
        print(f"seeded {template.name}: {len(template.items)} items")


async def run() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_all(session)


if __name__ == "__main__":
    asyncio.run(run())
