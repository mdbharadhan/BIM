from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compliance_standard import ComplianceStandard


class ComplianceStandardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, standard: ComplianceStandard) -> ComplianceStandard:
        self.db.add(standard)
        await self.db.commit()
        await self.db.refresh(standard)
        return standard

    async def get_by_id(self, standard_id: int) -> ComplianceStandard | None:
        result = await self.db.execute(
            select(ComplianceStandard).where(ComplianceStandard.id == standard_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> ComplianceStandard | None:
        result = await self.db.execute(
            select(ComplianceStandard).where(ComplianceStandard.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ComplianceStandard]:
        result = await self.db.execute(select(ComplianceStandard))
        return list(result.scalars().all())

    async def update(self, standard: ComplianceStandard, data: dict) -> ComplianceStandard:
        for key, value in data.items():
            setattr(standard, key, value)
        await self.db.commit()
        await self.db.refresh(standard)
        return standard

    async def delete(self, standard: ComplianceStandard) -> None:
        await self.db.delete(standard)
        await self.db.commit()
