"""Evaluate measurements against a standard's rules and record the results.

This sits *above* the compliance primitive, it does not change it. The primitive
stores whatever `result` it is given and never derives one (see CONTEXT.md); the
deciding happens here, and every check is written through ComplianceService so
the primitive stays the single writer.
"""

from app.domain.compliance_evaluation import (
    NON_NUMERIC_OPERATORS,
    RuleDefinitionError,
    Thresholds,
    evaluate_attestation,
    evaluate_numeric,
)
from app.domain.enums import ComplianceResult
from app.models.compliance_check import ComplianceCheck
from app.models.compliance_rule import ComplianceRule
from app.schemas.compliance_check import ComplianceCheckCreate
from app.schemas.compliance_evaluation import (
    ComplianceEvaluationRequest,
    ComplianceEvaluationResponse,
    SkippedRule,
)
from app.services.compliance_service import ComplianceService


class ComplianceEvaluationService:
    def __init__(self, compliance_service: ComplianceService):
        self.compliance = compliance_service

    async def evaluate(
        self, data: ComplianceEvaluationRequest
    ) -> ComplianceEvaluationResponse:
        # 404s if the standard doesn't exist, before anything is written.
        rules = await self.compliance.get_rules_by_standard(data.standard_id)

        checks: list[ComplianceCheck] = []
        skipped: list[SkippedRule] = []

        for rule in rules:
            outcome = self._resolve(rule, data)
            if isinstance(outcome, SkippedRule):
                skipped.append(outcome)
                continue

            result, measured_value = outcome
            check = await self.compliance.create_check(
                ComplianceCheckCreate(
                    entity_type=data.entity_type,
                    entity_id=data.entity_id,
                    rule_id=rule.id,
                    measured_value=measured_value,
                    result=result,
                    checked_by=data.checked_by,
                    notes=data.notes,
                )
            )
            checks.append(check)

        return ComplianceEvaluationResponse(
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            standard_id=data.standard_id,
            passed=sum(c.result is ComplianceResult.PASS_ for c in checks),
            failed=sum(c.result is ComplianceResult.FAIL for c in checks),
            skipped=len(skipped),
            checks=checks,
            skipped_rules=skipped,
        )

    def _resolve(
        self, rule: ComplianceRule, data: ComplianceEvaluationRequest
    ) -> tuple[ComplianceResult, float | None] | SkippedRule:
        """Decide one rule. Returns the result and the value to record, or a
        SkippedRule explaining why it could not be decided."""
        key = rule.parameter_name

        def skip(reason: str) -> SkippedRule:
            return SkippedRule(
                rule_id=rule.id, rule_name=rule.name, parameter_name=key, reason=reason
            )

        if key is None:
            return skip("rule has no parameter_name to match input against")

        if rule.operator in NON_NUMERIC_OPERATORS:
            if key not in data.attestations:
                return skip("non-numeric rule requires an attestation")
            return evaluate_attestation(data.attestations[key]), None

        if key not in data.measurements:
            return skip("not measured")

        measured_value = data.measurements[key]
        try:
            result = evaluate_numeric(
                measured_value,
                Thresholds(
                    operator=rule.operator,
                    threshold_value=rule.threshold_value,
                    threshold_min=rule.threshold_min,
                    threshold_max=rule.threshold_max,
                ),
            )
        except RuleDefinitionError as exc:
            # A malformed rule is a data problem, not a failed inspection —
            # recording it as a FAIL would blame the material for a bad seed.
            return skip(str(exc))

        return result, measured_value