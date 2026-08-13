from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compliance_check import ComplianceCheck
from app.models.compliance_rule import ComplianceRule
from app.models.compliance_standard import ComplianceStandard
from app.repositories.compliance_check_repository import ComplianceCheckRepository
from app.repositories.compliance_rule_repository import ComplianceRuleRepository
from app.repositories.compliance_standard_repository import ComplianceStandardRepository
from app.schemas.compliance_check import ComplianceCheckCreate
from app.schemas.compliance_rule import ComplianceRuleCreate, ComplianceRuleUpdate
from app.schemas.compliance_standard import ComplianceStandardCreate, ComplianceStandardUpdate


class ComplianceService:
    def __init__(self, db: AsyncSession):
        self.standard_repo = ComplianceStandardRepository(db)
        self.rule_repo = ComplianceRuleRepository(db)
        self.check_repo = ComplianceCheckRepository(db)

    # -- standards ----------------------------------------------------------

    async def create_standard(self, data: ComplianceStandardCreate) -> ComplianceStandard:
        standard = ComplianceStandard(**data.model_dump())
        return await self.standard_repo.create(standard)

    async def get_standard(self, standard_id: int) -> ComplianceStandard:
        standard = await self.standard_repo.get_by_id(standard_id)
        if not standard:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Standard not found")
        return standard

    async def get_all_standards(self) -> list[ComplianceStandard]:
        return await self.standard_repo.get_all()

    async def update_standard(
        self, standard_id: int, data: ComplianceStandardUpdate
    ) -> ComplianceStandard:
        standard = await self.get_standard(standard_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.standard_repo.update(standard, update_data)

    async def delete_standard(self, standard_id: int) -> None:
        standard = await self.get_standard(standard_id)
        await self.standard_repo.delete(standard)

    # -- rules ----------------------------------------------------------------

    async def create_rule(self, standard_id: int, data: ComplianceRuleCreate) -> ComplianceRule:
        await self.get_standard(standard_id)
        rule = ComplianceRule(standard_id=standard_id, **data.model_dump())
        return await self.rule_repo.create(rule)

    async def get_rule(self, rule_id: int) -> ComplianceRule:
        rule = await self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
        return rule

    async def get_rules_by_standard(self, standard_id: int) -> list[ComplianceRule]:
        await self.get_standard(standard_id)
        return await self.rule_repo.get_by_standard(standard_id)

    async def update_rule(self, rule_id: int, data: ComplianceRuleUpdate) -> ComplianceRule:
        rule = await self.get_rule(rule_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.rule_repo.update(rule, update_data)

    async def delete_rule(self, rule_id: int) -> None:
        rule = await self.get_rule(rule_id)
        await self.rule_repo.delete(rule)

    # -- checks ---------------------------------------------------------------

    async def create_check(self, data: ComplianceCheckCreate) -> ComplianceCheck:
        await self.get_rule(data.rule_id)
        check = ComplianceCheck(**data.model_dump())
        return await self.check_repo.create(check)

    async def get_check(self, check_id: int) -> ComplianceCheck:
        check = await self.check_repo.get_by_id(check_id)
        if not check:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check not found")
        return check

    async def get_all_checks(self) -> list[ComplianceCheck]:
        return await self.check_repo.get_all()

    async def get_checks_by_rule(self, rule_id: int) -> list[ComplianceCheck]:
        return await self.check_repo.get_by_rule(rule_id)

    async def get_checks_by_entity(self, entity_type: str, entity_id: int) -> list[ComplianceCheck]:
        return await self.check_repo.get_by_entity(entity_type, entity_id)
