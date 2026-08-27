"""Pure rule-evaluation logic — no database, no I/O.

Kept separate from the service so the decision "does 6.2% silt pass a <5% rule"
can be tested directly, without a session, a standard, or an entity. The service
layer handles persistence; this module only decides.
"""

import math
from dataclasses import dataclass

from app.domain.enums import ComplianceOperator, ComplianceResult

# Rules whose outcome cannot be computed from a number — a human (or, later, a
# document lookup or a vision model) has to supply the verdict.
NON_NUMERIC_OPERATORS = frozenset({ComplianceOperator.EXISTS, ComplianceOperator.CUSTOM})


class RuleDefinitionError(ValueError):
    """A rule whose operator and threshold columns disagree — e.g. `between`
    with no min/max. Raised rather than silently passing, since a rule that can
    never fail is worse than no rule at all."""


@dataclass(frozen=True)
class Thresholds:
    """The threshold columns of a ComplianceRule, decoupled from the ORM model
    so this module stays importable without SQLAlchemy."""

    operator: ComplianceOperator
    threshold_value: float | None = None
    threshold_min: float | None = None
    threshold_max: float | None = None


def evaluate_numeric(measured_value: float, thresholds: Thresholds) -> ComplianceResult:
    """Compare a measured value against a rule's thresholds.

    Raises RuleDefinitionError if the rule is not numerically evaluable.
    """
    op = thresholds.operator

    if op in NON_NUMERIC_OPERATORS:
        raise RuleDefinitionError(f"{op} rules cannot be evaluated from a measured value")

    if op is ComplianceOperator.BETWEEN:
        if thresholds.threshold_min is None or thresholds.threshold_max is None:
            raise RuleDefinitionError("between rule is missing threshold_min or threshold_max")
        passed = thresholds.threshold_min <= measured_value <= thresholds.threshold_max
        return ComplianceResult.PASS_ if passed else ComplianceResult.FAIL

    if thresholds.threshold_value is None:
        raise RuleDefinitionError(f"{op} rule is missing threshold_value")

    limit = thresholds.threshold_value
    match op:
        case ComplianceOperator.LT:
            passed = measured_value < limit
        case ComplianceOperator.LTE:
            passed = measured_value <= limit
        case ComplianceOperator.GT:
            passed = measured_value > limit
        case ComplianceOperator.GTE:
            passed = measured_value >= limit
        case ComplianceOperator.EQ:
            # Measured values arrive as floats from lab instruments; exact
            # equality would fail on 2.0999999999 vs 2.1.
            passed = math.isclose(measured_value, limit, rel_tol=1e-9, abs_tol=1e-9)
        case _:  # pragma: no cover - every operator is handled above
            raise RuleDefinitionError(f"unsupported operator {op}")

    return ComplianceResult.PASS_ if passed else ComplianceResult.FAIL


def evaluate_attestation(confirmed: bool) -> ComplianceResult:
    """Result for a non-numeric rule where a human confirmed or denied it."""
    return ComplianceResult.PASS_ if confirmed else ComplianceResult.FAIL