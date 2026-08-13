import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ComplianceOperator, ComplianceResult
from app.schemas.compliance_check import ComplianceCheckCreate
from app.schemas.compliance_rule import ComplianceRuleCreate
from app.schemas.compliance_standard import ComplianceStandardCreate
from app.services.compliance_service import ComplianceService


async def _make_rule(service: ComplianceService):
    standard = await service.create_standard(ComplianceStandardCreate(code="IS 383", name="Sand"))
    return await service.create_rule(
        standard.id,
        ComplianceRuleCreate(
            name="Silt content max",
            parameter_name="silt_content_percent",
            operator=ComplianceOperator.LT,
            threshold_value=5,
            unit="%",
        ),
    )


async def test_create_check_records_measured_value_and_result(db_session: AsyncSession):
    service = ComplianceService(db_session)
    rule = await _make_rule(service)

    check = await service.create_check(
        ComplianceCheckCreate(
            rule_id=rule.id,
            entity_type="material_delivery",
            entity_id=1,
            measured_value=3.2,
            result=ComplianceResult.PASS_,
        )
    )

    assert check.measured_value == 3.2
    assert check.result == ComplianceResult.PASS_


async def test_check_survives_rule_deletion(db_session: AsyncSession):
    service = ComplianceService(db_session)
    rule = await _make_rule(service)
    check = await service.create_check(
        ComplianceCheckCreate(
            rule_id=rule.id,
            entity_type="material_delivery",
            entity_id=1,
            measured_value=7.0,
            result=ComplianceResult.FAIL,
        )
    )

    await service.delete_rule(rule.id)

    # No relationship() links ComplianceCheck back to ComplianceRule, so the
    # SET NULL happens purely via the DB's FK constraint, invisible to the
    # session's identity map until the object is explicitly refreshed (the
    # session's expire_on_commit=False means it won't happen automatically).
    await db_session.refresh(check)
    assert check.rule_id is None
    assert check.result == ComplianceResult.FAIL


async def test_create_check_with_bogus_rule_raises_404(db_session: AsyncSession):
    service = ComplianceService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await service.create_check(
            ComplianceCheckCreate(
                rule_id=999, entity_type="material_delivery", entity_id=1, result="fail"
            )
        )
    assert exc_info.value.status_code == 404
