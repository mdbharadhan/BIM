"""Seed real compliance standards and rules.

Idempotent: safe to re-run. Standards are matched on `code`, rules on
(standard_id, name) — re-running updates values in place rather than creating
duplicates, so correcting a threshold is just an edit here plus a re-run.

Scope today is IS 383 fine aggregate plus four sustainability rating systems
(LEED, IGBC, GRIHA, BREEAM). Cement (IS 269 / IS 8112) and steel (IS 1786)
follow the same shape — add a StandardSeed and register it in ALL_STANDARDS.

Sustainability standards carry one deliberate omission: none of the four seed
a "certification level" rule (e.g. LEED Gold = 60-79 points). A level is a
rollup of every other credit's score, and ComplianceEvaluationService only
ever counts pass/fail/skip per rule — it has no notion of summing points. Each
standard below seeds its prerequisites and headline scored credits only, each
independently checkable; computing an overall certification level from those
checks is a future feature-layer concern; the primitive has no capability for
it today.

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

LEED_V4_BDC = StandardSeed(
    code="LEED v4 BD+C",
    name="LEED v4 for Building Design and Construction — New Construction",
    description=(
        "USGBC's LEED v4 Building Design and Construction rating system for new "
        "construction. Certified 40-49, Silver 50-59, Gold 60-79, Platinum 80-110 "
        "points — this seed does not model certification-level rollup, see module "
        "docstring; it covers prerequisites (mandatory, no points) and the entry "
        "threshold of several headline scored credits."
    ),
    rules=[
        RuleSeed(
            name="Fundamental Commissioning and Verification",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="fundamental_commissioning",
            rule_text=(
                "A commissioning authority is engaged and the Owner's Project "
                "Requirements and Basis of Design are reviewed before construction "
                "documents are finalized."
            ),
            needs_verification=False,
            source="LEED v4 BD+C EA Prerequisite: Fundamental Commissioning and Verification",
        ),
        RuleSeed(
            name="Minimum Energy Performance",
            operator=ComplianceOperator.GTE,
            parameter_name="energy_improvement_percent",
            threshold_value=5.0,
            unit="%",
            source="LEED v4 BD+C EA Prerequisite, improvement over ASHRAE 90.1-2010 baseline",
        ),
        RuleSeed(
            name="Building-Level Energy Metering",
            operator=ComplianceOperator.EXISTS,
            parameter_name="energy_metering_plan",
            rule_text=(
                "A building-level (or base building plus submeters for major end "
                "uses) energy metering plan is in place."
            ),
            needs_verification=False,
            source="LEED v4 BD+C EA Prerequisite: Building-Level Energy Metering",
        ),
        RuleSeed(
            name="Fundamental Refrigerant Management",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="refrigerant_management",
            rule_text=(
                "New heating, ventilating, air-conditioning and refrigeration "
                "equipment does not use CFC-based refrigerants."
            ),
            needs_verification=False,
            source="LEED v4 BD+C EA Prerequisite: Fundamental Refrigerant Management",
        ),
        RuleSeed(
            name="Minimum Indoor Water Use Reduction",
            operator=ComplianceOperator.GTE,
            parameter_name="indoor_water_reduction_percent",
            threshold_value=20.0,
            unit="%",
            source="LEED v4 BD+C WE Prerequisite 2, aggregate indoor water use reduction",
        ),
        RuleSeed(
            name="Construction Activity Pollution Prevention",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="pollution_prevention_plan",
            rule_text=(
                "An erosion, sedimentation, and pollution control plan is "
                "implemented for construction activities."
            ),
            needs_verification=False,
            source="LEED v4 BD+C SS Prerequisite: Construction Activity Pollution Prevention",
        ),
        RuleSeed(
            name="Storage and Collection of Recyclables",
            operator=ComplianceOperator.EXISTS,
            parameter_name="recyclables_storage",
            rule_text=(
                "Dedicated space for the collection and storage of recyclable "
                "materials serves the entire building."
            ),
            needs_verification=False,
            source="LEED v4 BD+C MR Prerequisite: Storage and Collection of Recyclables",
        ),
        RuleSeed(
            name="Construction and Demolition Waste Management Planning",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="cd_waste_management_plan",
            rule_text=(
                "A construction and demolition waste management plan identifies "
                "materials to be diverted and how."
            ),
            needs_verification=False,
            source="LEED v4 BD+C MR Prerequisite: C&D Waste Management Planning",
        ),
        RuleSeed(
            name="Minimum Indoor Air Quality Performance",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="min_iaq_performance",
            rule_text=(
                "Mechanical ventilation systems meet the minimum requirements of ASHRAE 62.1-2010."
            ),
            needs_verification=False,
            source="LEED v4 BD+C EQ Prerequisite: Minimum Indoor Air Quality Performance",
        ),
        RuleSeed(
            name="Environmental Tobacco Smoke Control",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="ets_control",
            rule_text=(
                "Smoking is prohibited inside the building; exterior smoking areas "
                "are located away from entries, air intakes, and operable windows."
            ),
            needs_verification=False,
            source="LEED v4 BD+C EQ Prerequisite: Environmental Tobacco Smoke Control",
        ),
        RuleSeed(
            name="Optimize Energy Performance (entry tier)",
            operator=ComplianceOperator.GTE,
            parameter_name="optimize_energy_performance_percent",
            threshold_value=6.0,
            unit="%",
            rule_text=(
                "Entry tier only: the full credit scales up to 18 points at higher "
                "improvement percentages; this rule checks the minimum entry point, "
                "not the full tiered scoring."
            ),
            source="LEED v4 BD+C EA Credit: Optimize Energy Performance",
        ),
        RuleSeed(
            name="Renewable Energy Production (entry tier)",
            operator=ComplianceOperator.GTE,
            parameter_name="renewable_energy_percent",
            threshold_value=1.0,
            unit="%",
            rule_text=(
                "Entry tier: on-site renewable energy meets at least 1% of building energy cost."
            ),
            source="LEED v4 BD+C EA Credit: Renewable Energy Production",
        ),
        RuleSeed(
            name="Indoor Water Use Reduction beyond prerequisite (entry tier)",
            operator=ComplianceOperator.GTE,
            parameter_name="indoor_water_reduction_credit_percent",
            threshold_value=25.0,
            unit="%",
            rule_text=(
                "Entry tier beyond the 20% prerequisite; full scale runs higher for more points."
            ),
            source="LEED v4 BD+C WE Credit: Indoor Water Use Reduction",
        ),
        RuleSeed(
            name="Construction and Demolition Waste Diversion (entry tier)",
            operator=ComplianceOperator.GTE,
            parameter_name="cd_waste_diversion_percent",
            threshold_value=50.0,
            unit="%",
            source="LEED v4 BD+C MR Credit: Construction and Demolition Waste Management",
        ),
    ],
)

IGBC_GREEN_NEW_BUILDINGS = StandardSeed(
    code="IGBC Green New Buildings",
    name="IGBC Green New Buildings Rating System",
    description=(
        "Indian Green Building Council's rating system for new buildings. "
        "Certified 50-59, Silver 60-69, Gold 70-79, Platinum 80+ points (of 100) "
        "— this seed does not model certification-level rollup, see module "
        "docstring; it covers mandatory requirements plus two headline credits."
    ),
    rules=[
        RuleSeed(
            name="Rainwater Harvesting, Roof and Non-Roof",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="rainwater_harvesting",
            rule_text=(
                "A rainwater harvesting system is designed to capture at least "
                "one day's rainfall from roof and non-roof runoff."
            ),
            needs_verification=False,
            source="IGBC Green New Buildings WC Mandatory Requirement 1",
        ),
        RuleSeed(
            name="Water Efficient Plumbing Fixtures",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="water_efficient_fixtures",
            rule_text="Plumbing fixtures installed meet IGBC's water-efficiency requirements.",
            needs_verification=False,
            source="IGBC Green New Buildings WC Mandatory Requirement 2",
        ),
        RuleSeed(
            name="Ozone Depleting Substances",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="ozone_depleting_substances",
            rule_text=(
                "HVAC&R equipment and fire suppression systems do not use "
                "ozone-depleting substances (CFCs, halons)."
            ),
            needs_verification=False,
            source="IGBC Green New Buildings EE Mandatory Requirement 1",
        ),
        RuleSeed(
            name="Minimum Energy Efficiency",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="min_energy_efficiency",
            rule_text=(
                "Building is designed to ECBC guidelines or ASHRAE Standard "
                "90.1-2010 whole-building simulation; exact minimum improvement "
                "percentage not yet confirmed against the published rating "
                "system, so this is recorded as an attestation rather than a "
                "numeric threshold."
            ),
            source="IGBC Green New Buildings EE Mandatory Requirement 2",
        ),
        RuleSeed(
            name="Commissioning Plan for Building Equipment and Systems",
            operator=ComplianceOperator.EXISTS,
            parameter_name="commissioning_plan",
            rule_text=(
                "A commissioning plan for major building equipment and systems "
                "is documented before construction."
            ),
            needs_verification=False,
            source="IGBC Green New Buildings EE Mandatory Requirement 3",
        ),
        RuleSeed(
            name="Renewable Energy Utilization (entry tier)",
            operator=ComplianceOperator.GTE,
            parameter_name="renewable_energy_percent",
            threshold_value=1.0,
            unit="%",
            rule_text=(
                "Entry tier for the renewable energy credit; full scale awards "
                "more points at higher renewable shares."
            ),
            source="IGBC Green New Buildings EE credit, renewable energy",
        ),
        RuleSeed(
            name="Organic and Inorganic Waste Management",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="waste_management",
            rule_text=(
                "Organic and inorganic waste generated on-site is segregated "
                "and treated or diverted appropriately."
            ),
            source="IGBC Green New Buildings SWM credit, waste segregation and treatment",
        ),
    ],
)

GRIHA = StandardSeed(
    code="GRIHA",
    name="GRIHA — Green Rating for Integrated Habitat Assessment",
    description=(
        "TERI/MNRE's national rating system for green buildings in India, adopted "
        "under 8 categories. Minimum 50 of 100 points required for any rating; "
        "1-star 50-60, 2-star 61-70, 3-star 71-80, 4-star 81-90, 5-star 91-100 — "
        "band table is corroborated by two sources but one unrelated example "
        "contradicted it, so it is not seeded as a rule (see module docstring) "
        "and every band figure below carries needs_verification=True."
    ),
    rules=[
        RuleSeed(
            name="Minimum Points for Certification",
            operator=ComplianceOperator.GTE,
            parameter_name="total_points",
            threshold_value=50.0,
            unit="points",
            rule_text="A project must score at least 50 of 100 points to receive any GRIHA rating.",
            source="GRIHA national rating system, minimum certification threshold",
        ),
        RuleSeed(
            name="Renewable Energy for Lighting",
            operator=ComplianceOperator.GTE,
            parameter_name="renewable_lighting_percent",
            threshold_value=10.0,
            unit="%",
            rule_text=(
                "At least 10% of the internal general lighting load is met from "
                "renewable energy sources (solar, wind, biomass, fuel cells)."
            ),
            source="GRIHA Criterion, renewable energy for lighting",
        ),
        RuleSeed(
            name="Solar Water Heating",
            operator=ComplianceOperator.GTE,
            parameter_name="solar_water_heating_percent",
            threshold_value=50.0,
            unit="%",
            rule_text=(
                "At least 50% of the annual water-heating energy requirement is "
                "supplied from renewable sources; exempt if daily hot water "
                "demand is under 500 L."
            ),
            source="GRIHA Criterion 19, solar water heating",
        ),
        RuleSeed(
            name="Rainwater Harvesting and Water Reuse",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="rainwater_harvesting_reuse",
            rule_text=(
                "Rainwater is recharged or reused on-site; exempt where the "
                "water table is already high."
            ),
            source="GRIHA Criterion 21, water recycle and reuse",
        ),
        RuleSeed(
            name="Sustainable Site Planning",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="sustainable_site_planning",
            rule_text=(
                "Site planning preserves topsoil, existing site features, and "
                "minimizes site disturbance per GRIHA's site planning criteria."
            ),
            source="GRIHA category: Sustainable Site Planning",
        ),
        RuleSeed(
            name="Indoor Air Quality",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="indoor_air_quality",
            rule_text=(
                "Ventilation and material choices meet GRIHA's indoor air quality requirements."
            ),
            source="GRIHA category: Indoor Air Quality",
        ),
    ],
)

BREEAM = StandardSeed(
    code="BREEAM",
    name="BREEAM — Building Research Establishment Environmental Assessment Method",
    description=(
        "BRE's UK-originated sustainability assessment across 9 weighted "
        "categories (Energy, Water, Transport, Management, Waste, Pollution, "
        "Health & Well-Being, Land Use & Ecology, Materials). Rating bands: "
        "Unclassified <30%, Pass >=30%, Good >=45%, Very Good >=55%, "
        "Excellent >=70%, Outstanding >=85% of the weighted score — not seeded "
        "as a rule, see module docstring. The rules below are one representative "
        "headline item per category, not the full credit set; BREEAM's real "
        "scoring spans many more sub-credits per category than modeled here."
    ),
    rules=[
        RuleSeed(
            name="Energy Performance Reduction",
            operator=ComplianceOperator.GTE,
            parameter_name="energy_improvement_percent",
            threshold_value=10.0,
            unit="%",
            rule_text=(
                "Representative Energy-category item: predicted energy "
                "performance improvement over a notional building baseline "
                "(Ene 01)."
            ),
            source="BREEAM category: Energy",
        ),
        RuleSeed(
            name="Water Consumption Reduction",
            operator=ComplianceOperator.GTE,
            parameter_name="water_consumption_reduction_percent",
            threshold_value=15.0,
            unit="%",
            rule_text=(
                "Representative Water-category item: reduction in water "
                "consumption against a baseline (Wat 01)."
            ),
            source="BREEAM category: Water",
        ),
        RuleSeed(
            name="Sustainable Transport Provision",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="sustainable_transport",
            rule_text=(
                "Site has access to public transport and provides cyclist "
                "facilities per BREEAM's transport criteria."
            ),
            source="BREEAM category: Transport",
        ),
        RuleSeed(
            name="Building User Guide and Commissioning",
            operator=ComplianceOperator.EXISTS,
            parameter_name="commissioning_and_user_guide",
            rule_text=(
                "A building user guide is provided and commissioning is planned and carried out."
            ),
            source="BREEAM category: Management",
        ),
        RuleSeed(
            name="Construction Waste Diversion",
            operator=ComplianceOperator.GTE,
            parameter_name="cd_waste_diversion_percent",
            threshold_value=50.0,
            unit="%",
            rule_text=(
                "Representative Waste-category item: proportion of "
                "construction waste diverted from landfill."
            ),
            source="BREEAM category: Waste",
        ),
        RuleSeed(
            name="Surface Water Runoff Control",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="surface_water_runoff_control",
            rule_text=(
                "Surface water run-off is managed to reduce flood risk, per "
                "BREEAM's pollution criteria."
            ),
            source="BREEAM category: Pollution",
        ),
        RuleSeed(
            name="Indoor Air Quality and Thermal Comfort",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="iaq_thermal_comfort",
            rule_text=(
                "Ventilation, daylighting, and thermal comfort meet BREEAM's "
                "Health & Well-Being requirements."
            ),
            source="BREEAM category: Health & Well-Being",
        ),
        RuleSeed(
            name="Ecological Value Protection",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="ecological_value_protection",
            rule_text=(
                "Existing ecological features on the site are protected from construction damage."
            ),
            source="BREEAM category: Land Use & Ecology",
        ),
        RuleSeed(
            name="Responsible Sourcing of Materials",
            operator=ComplianceOperator.CUSTOM,
            parameter_name="responsible_sourcing",
            rule_text=(
                "Key building materials are responsibly sourced per a "
                "recognized certification scheme."
            ),
            source="BREEAM category: Materials",
        ),
    ],
)

ALL_STANDARDS: list[StandardSeed] = [
    IS383_FINE_AGGREGATE,
    LEED_V4_BDC,
    IGBC_GREEN_NEW_BUILDINGS,
    GRIHA,
    BREEAM,
]


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
