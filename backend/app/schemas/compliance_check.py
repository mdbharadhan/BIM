from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import ComplianceResult
from app.schemas.mixins import EntityRef


class ComplianceCheckCreate(EntityRef):
    rule_id: int
    measured_value: float | None = None
    result: ComplianceResult
    checked_by: str | None = None
    notes: str | None = None


class ComplianceCheckResponse(BaseModel):
    id: int
    entity_type: str | None
    entity_id: int | None
    rule_id: int | None
    measured_value: float | None
    result: ComplianceResult
    checked_by: str | None
    checked_at: datetime
    notes: str | None

    model_config = ConfigDict(from_attributes=True)
