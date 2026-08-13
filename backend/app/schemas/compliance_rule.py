from pydantic import BaseModel, ConfigDict

from app.domain.enums import ComplianceOperator


class ComplianceRuleCreate(BaseModel):
    name: str
    parameter_name: str | None = None
    operator: ComplianceOperator
    threshold_value: float | None = None
    threshold_min: float | None = None
    threshold_max: float | None = None
    unit: str | None = None
    rule_text: str | None = None


class ComplianceRuleUpdate(BaseModel):
    name: str | None = None
    parameter_name: str | None = None
    operator: ComplianceOperator | None = None
    threshold_value: float | None = None
    threshold_min: float | None = None
    threshold_max: float | None = None
    unit: str | None = None
    rule_text: str | None = None


class ComplianceRuleResponse(BaseModel):
    id: int
    standard_id: int
    name: str
    parameter_name: str | None
    operator: ComplianceOperator
    threshold_value: float | None
    threshold_min: float | None
    threshold_max: float | None
    unit: str | None
    rule_text: str | None

    model_config = ConfigDict(from_attributes=True)
