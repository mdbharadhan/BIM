from app.domain.enums import ComplianceOperator
from app.repositories.compliance_rule_repository import ComplianceRuleRepository
from app.repositories.compliance_standard_repository import ComplianceStandardRepository
from app.seeds.compliance import ALL_STANDARDS, IS383_FINE_AGGREGATE, seed_all, seed_standard


async def test_seed_creates_standard_and_rules(db_session):
    standard = await seed_standard(db_session, IS383_FINE_AGGREGATE)

    assert standard.code == IS383_FINE_AGGREGATE.code
    rules = await ComplianceRuleRepository(db_session).get_by_standard(standard.id)
    assert len(rules) == len(IS383_FINE_AGGREGATE.rules)


async def test_seed_is_idempotent(db_session):
    await seed_all(db_session)
    await seed_all(db_session)

    standards = await ComplianceStandardRepository(db_session).get_all()
    assert len(standards) == len(ALL_STANDARDS)

    rules = await ComplianceRuleRepository(db_session).get_by_standard(standards[0].id)
    assert len(rules) == len(IS383_FINE_AGGREGATE.rules)


async def test_rerun_updates_changed_threshold(db_session):
    standard = await seed_standard(db_session, IS383_FINE_AGGREGATE)
    repo = ComplianceRuleRepository(db_session)

    rules = await repo.get_by_standard(standard.id)
    silt = next(r for r in rules if r.name == "Silt content max")
    await repo.update(silt, {"threshold_value": 99.0})

    await seed_standard(db_session, IS383_FINE_AGGREGATE)

    rules = await repo.get_by_standard(standard.id)
    silt = next(r for r in rules if r.name == "Silt content max")
    assert silt.threshold_value == 3.0


async def test_numeric_rules_carry_a_threshold(db_session):
    """A numeric operator with no threshold would silently never evaluate."""
    for seed in ALL_STANDARDS:
        for rule in seed.rules:
            if rule.operator in (
                ComplianceOperator.LT,
                ComplianceOperator.LTE,
                ComplianceOperator.GT,
                ComplianceOperator.GTE,
                ComplianceOperator.EQ,
            ):
                assert rule.threshold_value is not None, rule.name
            if rule.operator is ComplianceOperator.BETWEEN:
                assert rule.threshold_min is not None, rule.name
                assert rule.threshold_max is not None, rule.name
            if rule.operator in (ComplianceOperator.EXISTS, ComplianceOperator.CUSTOM):
                assert rule.rule_text, rule.name


async def test_rule_parameter_names_are_unique(db_session):
    """The evaluator will look rules up by parameter_name — duplicates would be
    ambiguous."""
    for seed in ALL_STANDARDS:
        names = [r.parameter_name for r in seed.rules if r.parameter_name]
        assert len(names) == len(set(names)), seed.code