from pydantic import BaseModel, ConfigDict, Field

from app.schemas.compliance_check import ComplianceCheckResponse
from app.schemas.mixins import EntityRef


class ComplianceEvaluationRequest(EntityRef):
    """Evaluate a batch of measurements for one entity against one standard.

    `measurements` is keyed by ComplianceRule.parameter_name — the seeded rules
    define those keys (e.g. "silt_content_percent").

    `attestations` carries verdicts for rules that no number can settle:
    `exists` rules (is the Material Test Certificate on file?) and `custom`
    rules (did the organic-impurities colour test pass?). These are supplied by
    whoever performs the check today; the MTC one will later be answered
    automatically by the document register.
    """

    standard_id: int
    measurements: dict[str, float] = Field(default_factory=dict)
    attestations: dict[str, bool] = Field(default_factory=dict)
    checked_by: str | None = None
    notes: str | None = None


class SkippedRule(BaseModel):
    """A rule the evaluation could not settle, and why. Surfaced rather than
    silently dropped — an unmeasured parameter is a gap in the inspection, not
    a pass."""

    rule_id: int
    rule_name: str
    parameter_name: str | None
    reason: str


class ComplianceEvaluationResponse(BaseModel):
    entity_type: str
    entity_id: int
    standard_id: int
    passed: int
    failed: int
    skipped: int
    checks: list[ComplianceCheckResponse]
    skipped_rules: list[SkippedRule]

    model_config = ConfigDict(from_attributes=True)