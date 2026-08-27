from app.domain.enums import ComplianceOperator
from app.repositories.compliance_rule_repository import ComplianceRuleRepository
from app.repositories.compliance_standard_repository import ComplianceStandardRepository
from app.seeds.compliance import (
    BREEAM,
    GRIHA,
    IGBC_GREEN_NEW_BUILDINGS,
    LEED_V4_BDC,
    seed_all,
    seed_standard,
)

SUSTAINABILITY_STANDARDS = [LEED_V4_BDC, IGBC_GREEN_NEW_BUILDINGS, GRIHA, BREEAM]


async def test_each_sustainability_standard_seeds_its_rules(db_session):
    for seed in SUSTAINABILITY_STANDARDS:
        standard = await seed_standard(db_session, seed)
        rules = await ComplianceRuleRepository(db_session).get_by_standard(standard.id)
        assert len(rules) == len(seed.rules), seed.code


async def test_sustainability_seeds_are_idempotent(db_session):
    await seed_all(db_session)
    await seed_all(db_session)

    standards = await ComplianceStandardRepository(db_session).get_all()
    codes = {s.code for s in standards}
    for seed in SUSTAINABILITY_STANDARDS:
        assert seed.code in codes

    rule_repo = ComplianceRuleRepository(db_session)
    for seed in SUSTAINABILITY_STANDARDS:
        standard = next(s for s in standards if s.code == seed.code)
        rules = await rule_repo.get_by_standard(standard.id)
        assert len(rules) == len(seed.rules), seed.code


async def test_no_standard_seeds_a_certification_level_rollup_rule():
    """Deliberate omission per the module docstring: the evaluator only counts
    pass/fail/skip per rule, it never sums points, so no rule here should
    represent a certification-level band (Certified/Silver/Gold/Platinum/star)."""
    banned_terms = (
        "certified level",
        "silver level",
        "gold level",
        "platinum level",
        "star rating",
    )
    for seed in SUSTAINABILITY_STANDARDS:
        for rule in seed.rules:
            lowered = rule.name.lower()
            assert not any(term in lowered for term in banned_terms), (seed.code, rule.name)


async def test_griha_minimum_points_rule_is_the_only_total_points_rule():
    total_points_rules = [r for r in GRIHA.rules if r.parameter_name == "total_points"]
    assert len(total_points_rules) == 1
    assert total_points_rules[0].operator is ComplianceOperator.GTE
    assert total_points_rules[0].threshold_value == 50.0


async def test_leed_prerequisites_and_credits_use_distinct_parameter_names():
    """Regression guard: Minimum Energy Performance and Optimize Energy
    Performance both measure an energy-improvement percentage but at
    different thresholds — they must not share a parameter_name, or the
    evaluator can't tell which threshold a measurement is being checked
    against."""
    names = [r.parameter_name for r in LEED_V4_BDC.rules if r.parameter_name]
    assert len(names) == len(set(names))
