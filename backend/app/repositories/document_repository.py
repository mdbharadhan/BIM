from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import DocumentStatus
from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, document: Document) -> Document:
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_by_id(self, document_id: int) -> Document | None:
        result = await self.db.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def search(
        self, category: str | None = None, doc_status: DocumentStatus | None = None
    ) -> list[Document]:
        query = select(Document)
        if category is not None:
            query = query.where(Document.category == category)
        if doc_status is not None:
            query = query.where(Document.status == doc_status)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_family(self, family_id: int) -> list[Document]:
        result = await self.db.execute(
            select(Document).where(Document.family_id == family_id).order_by(Document.version)
        )
        return list(result.scalars().all())

    async def get_by_entity(self, entity_type: str, entity_id: int) -> list[Document]:
        result = await self.db.execute(
            select(Document).where(
                Document.entity_type == entity_type, Document.entity_id == entity_id
            )
        )
        return list(result.scalars().all())

    async def update(self, document: Document, data: dict) -> Document:
        for key, value in data.items():
            setattr(document, key, value)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete(self, document: Document) -> None:
        await self.db.delete(document)
        await self.db.commit()
