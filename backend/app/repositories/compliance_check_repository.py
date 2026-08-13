from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compliance_check import ComplianceCheck


class ComplianceCheckRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, check: ComplianceCheck) -> ComplianceCheck:
        self.db.add(check)
        await self.db.commit()
        await self.db.refresh(check)
        return check

    async def get_by_id(self, check_id: int) -> ComplianceCheck | None:
        result = await self.db.execute(
            select(ComplianceCheck).where(ComplianceCheck.id == check_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ComplianceCheck]:
        result = await self.db.execute(select(ComplianceCheck))
        return list(result.scalars().all())

    async def get_by_rule(self, rule_id: int) -> list[ComplianceCheck]:
        result = await self.db.execute(
            select(ComplianceCheck).where(ComplianceCheck.rule_id == rule_id)
        )
        return list(result.scalars().all())

    async def get_by_entity(self, entity_type: str, entity_id: int) -> list[ComplianceCheck]:
        result = await self.db.execute(
            select(ComplianceCheck).where(
                ComplianceCheck.entity_type == entity_type, ComplianceCheck.entity_id == entity_id
            )
        )
        return list(result.scalars().all())
