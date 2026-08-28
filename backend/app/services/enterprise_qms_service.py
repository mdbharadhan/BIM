"""Enterprise QMS's registers — a thin read layer over the Document primitive,
not a new primitive. Writes (creating or updating a register) go through the
existing DocumentService directly with `category` set to a RegisterCategory
value; this only adds "what's current" and "show its history" convenience.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enterprise_qms import RegisterCategory, pick_most_recent
from app.domain.enums import DocumentStatus
from app.models.document import Document
from app.services.document_service import DocumentService


class EnterpriseQmsService:
    def __init__(self, db: AsyncSession):
        self.documents = DocumentService(db)

    async def get_current_or_none(self, category: RegisterCategory) -> Document | None:
        current = await self.documents.search(
            category=category.value, doc_status=DocumentStatus.CURRENT
        )
        return pick_most_recent(current)

    async def get_current(self, category: RegisterCategory) -> Document:
        document = await self.get_current_or_none(category)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No current {category.value} document found",
            )
        return document

    async def get_history(self, category: RegisterCategory) -> list[Document]:
        current = await self.get_current_or_none(category)
        if current is None:
            return []
        if current.family_id is None:
            return [current]
        return await self.documents.get_versions(current.id)
