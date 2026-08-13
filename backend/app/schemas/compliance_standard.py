from pydantic import BaseModel, ConfigDict


class ComplianceStandardCreate(BaseModel):
    code: str
    name: str
    description: str | None = None


class ComplianceStandardUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None


class ComplianceStandardResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)
