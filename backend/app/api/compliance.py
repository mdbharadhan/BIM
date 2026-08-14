from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.compliance_check import ComplianceCheck
from app.models.compliance_rule import ComplianceRule
from app.models.compliance_standard import ComplianceStandard
from app.schemas.compliance_check import ComplianceCheckCreate, ComplianceCheckResponse
from app.schemas.compliance_evaluation import (
    ComplianceEvaluationRequest,
    ComplianceEvaluationResponse,
)
from app.schemas.compliance_rule import (
    ComplianceRuleCreate,
    ComplianceRuleResponse,
    ComplianceRuleUpdate,
)
from app.schemas.compliance_standard import (
    ComplianceStandardCreate,
    ComplianceStandardResponse,
    ComplianceStandardUpdate,
)
from app.services.compliance_evaluation_service import ComplianceEvaluationService
from app.services.compliance_service import ComplianceService

router = APIRouter(tags=["Compliance"])


@router.post("/compliance-standards", response_model=ComplianceStandardResponse, status_code=201)
async def create_standard(
    data: ComplianceStandardCreate, db: AsyncSession = Depends(get_db)
) -> ComplianceStandard:
    return await ComplianceService(db).create_standard(data)


@router.get("/compliance-standards", response_model=list[ComplianceStandardResponse])
async def list_standards(db: AsyncSession = Depends(get_db)) -> list[ComplianceStandard]:
    return await ComplianceService(db).get_all_standards()


@router.get("/compliance-standards/{standard_id}", response_model=ComplianceStandardResponse)
async def get_standard(standard_id: int, db: AsyncSession = Depends(get_db)) -> ComplianceStandard:
    return await ComplianceService(db).get_standard(standard_id)


@router.put("/compliance-standards/{standard_id}", response_model=ComplianceStandardResponse)
async def update_standard(
    standard_id: int, data: ComplianceStandardUpdate, db: AsyncSession = Depends(get_db)
) -> ComplianceStandard:
    return await ComplianceService(db).update_standard(standard_id, data)


@router.delete("/compliance-standards/{standard_id}", status_code=204)
async def delete_standard(standard_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await ComplianceService(db).delete_standard(standard_id)


@router.post(
    "/compliance-standards/{standard_id}/rules",
    response_model=ComplianceRuleResponse,
    status_code=201,
)
async def create_rule(
    standard_id: int, data: ComplianceRuleCreate, db: AsyncSession = Depends(get_db)
) -> ComplianceRule:
    return await ComplianceService(db).create_rule(standard_id, data)


@router.get(
    "/compliance-standards/{standard_id}/rules", response_model=list[ComplianceRuleResponse]
)
async def list_rules_by_standard(
    standard_id: int, db: AsyncSession = Depends(get_db)
) -> list[ComplianceRule]:
    return await ComplianceService(db).get_rules_by_standard(standard_id)


@router.get("/compliance-rules/{rule_id}", response_model=ComplianceRuleResponse)
async def get_rule(rule_id: int, db: AsyncSession = Depends(get_db)) -> ComplianceRule:
    return await ComplianceService(db).get_rule(rule_id)


@router.put("/compliance-rules/{rule_id}", response_model=ComplianceRuleResponse)
async def update_rule(
    rule_id: int, data: ComplianceRuleUpdate, db: AsyncSession = Depends(get_db)
) -> ComplianceRule:
    return await ComplianceService(db).update_rule(rule_id, data)


@router.delete("/compliance-rules/{rule_id}", status_code=204)
async def delete_rule(rule_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await ComplianceService(db).delete_rule(rule_id)


@router.post("/compliance-checks", response_model=ComplianceCheckResponse, status_code=201)
async def create_check(
    data: ComplianceCheckCreate, db: AsyncSession = Depends(get_db)
) -> ComplianceCheck:
    return await ComplianceService(db).create_check(data)


@router.get("/compliance-checks", response_model=list[ComplianceCheckResponse])
async def list_checks(db: AsyncSession = Depends(get_db)) -> list[ComplianceCheck]:
    return await ComplianceService(db).get_all_checks()


@router.get("/compliance-checks/{check_id}", response_model=ComplianceCheckResponse)
async def get_check(check_id: int, db: AsyncSession = Depends(get_db)) -> ComplianceCheck:
    return await ComplianceService(db).get_check(check_id)


@router.get(
    "/compliance-rules/{rule_id}/checks", response_model=list[ComplianceCheckResponse]
)
async def list_checks_by_rule(
    rule_id: int, db: AsyncSession = Depends(get_db)
) -> list[ComplianceCheck]:
    return await ComplianceService(db).get_checks_by_rule(rule_id)


@router.post(
    "/compliance-evaluations", response_model=ComplianceEvaluationResponse, status_code=201
)
async def evaluate_compliance(
    data: ComplianceEvaluationRequest, db: AsyncSession = Depends(get_db)
) -> ComplianceEvaluationResponse:
    return await ComplianceEvaluationService(ComplianceService(db)).evaluate(data)


@router.get(
    "/entities/{entity_type}/{entity_id}/compliance-checks",
    response_model=list[ComplianceCheckResponse],
)
async def get_checks_by_entity(
    entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db)
) -> list[ComplianceCheck]:
    return await ComplianceService(db).get_checks_by_entity(entity_type, entity_id)