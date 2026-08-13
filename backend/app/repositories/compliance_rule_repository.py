from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compliance_rule import ComplianceRule


class ComplianceRuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, rule: ComplianceRule) -> ComplianceRule:
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def get_by_id(self, rule_id: int) -> ComplianceRule | None:
        result = await self.db.execute(select(ComplianceRule).where(ComplianceRule.id == rule_id))
        return result.scalar_one_or_none()

    async def get_by_standard(self, standard_id: int) -> list[ComplianceRule]:
        result = await self.db.execute(
            select(ComplianceRule).where(ComplianceRule.standard_id == standard_id)
        )
        return list(result.scalars().all())

    async def update(self, rule: ComplianceRule, data: dict) -> ComplianceRule:
        for key, value in data.items():
            setattr(rule, key, value)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def delete(self, rule: ComplianceRule) -> None:
        await self.db.delete(rule)
        await self.db.commit()
