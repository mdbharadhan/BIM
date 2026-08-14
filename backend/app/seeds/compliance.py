"""Seed real compliance standards and rules.

Idempotent: safe to re-run. Standards are matched on `code`, rules on
(standard_id, name) — re-running updates values in place rather than creating
duplicates, so correcting a threshold is just an edit here plus a re-run.

Scope today is IS 383 fine aggregate only, because that is the only rule set the
sand-delivery flow actually exercises. Cement (IS 269 / IS 8112), steel
(IS 1786) and sustainability (LEED / IGBC / GRIHA / BREEAM) follow the same
shape — add a StandardSeed and register it in ALL_STANDARDS.

    python -m app.seeds.compliance          # run from backend/

THRESHOLD VALUES ARE NOT YET VERIFIED against the published standard. Every rule
carrying needs_verification=True is a placeholder pending sign-off; the runner
prints them on every run. Do not treat a seeded number as authoritative until
the flag is cleared.
"""

import asyncio
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import AsyncSessionLocal, Base, engine
from app.domain.enums import ComplianceOperator
from app.models.compliance_rule import ComplianceRule
from app.models.compliance_standard import ComplianceStandard
from app.repositories.compliance_rule_repository import ComplianceRuleRepository
from app.repositories.compliance_standard_repository import ComplianceStandardRepository


@dataclass(frozen=True)
class RuleSeed:
    """One rule as authored here.

    `needs_verification` and `source` are authoring metadata only — they are not
    persisted, since ComplianceRule has nowhere to put them. They exist so the
    runner can report which numbers are still unconfirmed.
    """

    name: str
    operator: ComplianceOperator
    parameter_name: str | None = None
    threshold_value: float | None = None
    threshold_min: float | None = None
    threshold_max: float | None = None
    unit: str | None = None
    rule_text: str | None = None
    needs_verification: bool = True
    source: str = ""

    def to_columns(self) -> dict:
        return {
            "name": self.name,
            "parameter_name": self.parameter_name,
            "operator": self.operator,
            "threshold_value": self.threshold_value,
            "threshold_min": self.threshold_min,
            "threshold_max": self.threshold_max,
            "unit": self.unit,
            "rule_text": self.rule_text,
        }


@dataclass(frozen=True)
class StandardSeed:
    code: str
    name: str
    description: str | None
    rules: list[RuleSeed] = field(default_factory=list)


# Named "IS 383 (Fine Aggregate)" rather than plain "IS 383": the published
# standard covers both fine and coarse aggregate, and several limits differ
# between them. Coarse aggregate becomes a sibling StandardSeed later, so a sand
# delivery is never evaluated against a coarse-aggregate limit.
IS383_FINE_AGGREGATE = StandardSeed(
    code="IS 383 (Fine Aggregate)",
    name="IS 383 — Specification for Coarse and Fine Aggregates (Fine Aggregate)",
    description=(
        "Indian Standard specification for aggregates from natural sources for concrete. "
        "This standard record carries the fine-aggregate (sand) acceptance rules only."
    ),
    rules=[
        RuleSeed(
            name="Grading conforms to a recognised zone",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="grading_zone",
            rule_text=(
                "Sieve analysis result shall conform to one of the fine aggregate grading "
                "zones defined in IS 383. Record the zone determined."
            ),
            source="IS 383 grading zone table",
        ),
        RuleSeed(
            name="Fineness modulus within range",
            operator=ComplianceOperator.BETWEEN,
            parameter_name="fineness_modulus",
            threshold_min=2.0,
            threshold_max=3.5,
            unit="",
            source="Typical acceptance range — confirm project specification",
        ),
        RuleSeed(
            name="Silt content max",
            operator=ComplianceOperator.LTE,
            parameter_name="silt_content_percent",
            threshold_value=3.0,
            unit="%",
            source=(
                "Field sedimentation test. Commonly 3% for natural sand; project "
                "specifications often allow more for manufactured sand"
            ),
        ),
        RuleSeed(
            name="Clay lumps max",
            operator=ComplianceOperator.LTE,
            parameter_name="clay_lumps_percent",
            threshold_value=1.0,
            unit="%",
            source="IS 383 deleterious materials table",
        ),
        RuleSeed(
            name="Material finer than 75 micron max (uncrushed)",
            operator=ComplianceOperator.LTE,
            parameter_name="finer_than_75_micron_percent",
            threshold_value=3.0,
            unit="%",
            source="IS 383 deleterious materials table — uncrushed fine aggregate",
        ),
        RuleSeed(
            name="Material finer than 75 micron max (crushed)",
            operator=ComplianceOperator.LTE,
            parameter_name="finer_than_75_micron_crushed_percent",
            threshold_value=15.0,
            unit="%",
            source="IS 383 deleterious materials table — crushed fine aggregate",
        ),
        RuleSeed(
            name="Organic impurities acceptable",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="organic_impurities",
            rule_text=(
                "Colourimetric test result shall not be darker than the reference standard "
                "solution. Record pass/fail against the reference."
            ),
            source="IS 2386 Part 2 colourimetric test",
        ),
        RuleSeed(
            name="Chloride content max",
            operator=ComplianceOperator.LTE,
            parameter_name="chloride_content_percent",
            threshold_value=0.04,
            unit="%",
            source="Acid-soluble chloride as Cl by mass — limit differs for prestressed work",
        ),
        RuleSeed(
            name="Sulfate content max",
            operator=ComplianceOperator.LTE,
            parameter_name="sulfate_content_percent",
            threshold_value=0.4,
            unit="%",
            source="Acid-soluble sulfate as SO3 by mass",
        ),
        RuleSeed(
            name="Specific gravity within range",
            operator=ComplianceOperator.BETWEEN,
            parameter_name="specific_gravity",
            threshold_min=2.4,
            threshold_max=2.9,
            unit="",
            source="Typical range for natural sand — not a published code limit",
        ),
        RuleSeed(
            name="Water absorption max",
            operator=ComplianceOperator.LTE,
            parameter_name="water_absorption_percent",
            threshold_value=2.0,
            unit="%",
            source="Common project specification limit",
        ),
        RuleSeed(
            name="Moisture content recorded",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="moisture_content_percent",
            unit="%",
            rule_text=(
                "Surface moisture shall be measured and recorded so batching water can be "
                "corrected. Not a rejection criterion on its own."
            ),
            needs_verification=False,
            source="Batching correction requirement, not an acceptance limit",
        ),
        RuleSeed(
            name="Bulk density recorded",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="bulk_density_kg_m3",
            unit="kg/m3",
            rule_text=(
                "Loose and compacted bulk density shall be measured and recorded for mix "
                "design. Not a rejection criterion on its own."
            ),
            needs_verification=False,
            source="Mix design input, not an acceptance limit",
        ),
        RuleSeed(
            name="Particle shape and angularity acceptable",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="particle_shape",
            rule_text=(
                "Particle shape shall be assessed and recorded. Excessively flaky or "
                "elongated particles are grounds for rejection."
            ),
            needs_verification=False,
            source="Visual/petrographic assessment",
        ),
        RuleSeed(
            name="Material Test Certificate provided",
            operator=ComplianceOperator.EXISTS,
            parameter_name="material_test_certificate",
            rule_text=(
                "A current Material Test Certificate shall be on file for this delivery, "
                "attached in the document register."
            ),
            needs_verification=False,
            source="Source approval and traceability",
        ),
        RuleSeed(
            name="Source approved",
            operator=ComplianceOperator.EXISTS,
            parameter_name="source_approval",
            rule_text=(
                "The supply source shall appear on the approved source list, with an "
                "approval document on file."
            ),
            needs_verification=False,
            source="Source approval and traceability",
        ),
    ],
)

ALL_STANDARDS: list[StandardSeed] = [IS383_FINE_AGGREGATE]


async def seed_standard(db: AsyncSession, seed: StandardSeed) -> ComplianceStandard:
    """Upsert one standard and its rules. Returns the persisted standard."""
    standard_repo = ComplianceStandardRepository(db)
    rule_repo = ComplianceRuleRepository(db)

    standard = await standard_repo.get_by_code(seed.code)
    if standard is None:
        standard = await standard_repo.create(
            ComplianceStandard(code=seed.code, name=seed.name, description=seed.description)
        )
    else:
        standard = await standard_repo.update(
            standard, {"name": seed.name, "description": seed.description}
        )

    existing = {rule.name: rule for rule in await rule_repo.get_by_standard(standard.id)}
    for rule_seed in seed.rules:
        columns = rule_seed.to_columns()
        if rule_seed.name in existing:
            await rule_repo.update(existing[rule_seed.name], columns)
        else:
            await rule_repo.create(ComplianceRule(standard_id=standard.id, **columns))

    return standard


async def seed_all(db: AsyncSession) -> None:
    for seed in ALL_STANDARDS:
        standard = await seed_standard(db, seed)
        print(f"seeded {standard.code}: {len(seed.rules)} rules")


def _print_verification_report() -> None:
    unverified = [
        (seed.code, rule)
        for seed in ALL_STANDARDS
        for rule in seed.rules
        if rule.needs_verification
    ]
    if not unverified:
        return
    print(f"\n{len(unverified)} threshold(s) still need verification:")
    for code, rule in unverified:
        print(f"  [{code}] {rule.name} — {rule.source}")


async def run() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_all(session)
    _print_verification_report()


if __name__ == "__main__":
    asyncio.run(run())