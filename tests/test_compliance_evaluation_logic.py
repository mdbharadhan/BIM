import pytest

from app.domain.compliance_evaluation import (
    RuleDefinitionError,
    Thresholds,
    evaluate_attestation,
    evaluate_numeric,
)
from app.domain.enums import ComplianceOperator, ComplianceResult

PASS = ComplianceResult.PASS_
FAIL = ComplianceResult.FAIL


@pytest.mark.parametrize(
    ("operator", "measured", "limit", "expected"),
    [
        (ComplianceOperator.LT, 4.9, 5.0, PASS),
        (ComplianceOperator.LT, 5.0, 5.0, FAIL),
        (ComplianceOperator.LTE, 5.0, 5.0, PASS),
        (ComplianceOperator.LTE, 5.1, 5.0, FAIL),
        (ComplianceOperator.GT, 5.1, 5.0, PASS),
        (ComplianceOperator.GT, 5.0, 5.0, FAIL),
        (ComplianceOperator.GTE, 5.0, 5.0, PASS),
        (ComplianceOperator.GTE, 4.9, 5.0, FAIL),
        (ComplianceOperator.EQ, 5.0, 5.0, PASS),
        (ComplianceOperator.EQ, 5.5, 5.0, FAIL),
    ],
)
def test_single_threshold_operators(operator, measured, limit, expected):
    thresholds = Thresholds(operator=operator, threshold_value=limit)
    assert evaluate_numeric(measured, thresholds) is expected


def test_boundary_is_the_difference_between_lt_and_lte():
    """The silt rule is lte 3.0 — exactly 3.0 must pass, not fail."""
    at_limit = 3.0
    lte = Thresholds(ComplianceOperator.LTE, threshold_value=3.0)
    lt = Thresholds(ComplianceOperator.LT, threshold_value=3.0)
    assert evaluate_numeric(at_limit, lte) is PASS
    assert evaluate_numeric(at_limit, lt) is FAIL


def test_eq_tolerates_float_representation_error():
    thresholds = Thresholds(ComplianceOperator.EQ, threshold_value=2.1)
    assert evaluate_numeric(0.7 + 0.7 + 0.7, thresholds) is PASS


@pytest.mark.parametrize(
    ("measured", "expected"),
    [(2.0, PASS), (2.75, PASS), (3.5, PASS), (1.9, FAIL), (3.6, FAIL)],
)
def test_between_is_inclusive(measured, expected):
    thresholds = Thresholds(ComplianceOperator.BETWEEN, threshold_min=2.0, threshold_max=3.5)
    assert evaluate_numeric(measured, thresholds) is expected


def test_attestation():
    assert evaluate_attestation(True) is PASS
    assert evaluate_attestation(False) is FAIL


@pytest.mark.parametrize(
    "thresholds",
    [
        Thresholds(ComplianceOperator.LTE),
        Thresholds(ComplianceOperator.BETWEEN, threshold_min=2.0),
        Thresholds(ComplianceOperator.BETWEEN, threshold_max=3.5),
        Thresholds(ComplianceOperator.EXISTS),
        Thresholds(ComplianceOperator.CUSTOM),
    ],
)
def test_unevaluable_rules_raise(thresholds):
    """A rule that can never fail is worse than no rule — refuse it loudly."""
    with pytest.raises(RuleDefinitionError):
        evaluate_numeric(1.0, thresholds)