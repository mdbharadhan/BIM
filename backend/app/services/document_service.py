from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import DocumentStatus
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentVersionCreate


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.repo = DocumentRepository(db)

    async def create(self, data: DocumentCreate) -> Document:
        document = Document(
            title=data.title,
            category=data.category,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            file_ref=data.file_ref,
            uploaded_by=data.uploaded_by,
            status=data.status,
        )
        document = await self.repo.create(document)
        # First version of a new family: the family is identified by its own id.
        return await self.repo.update(document, {"family_id": document.id})

    async def get(self, document_id: int) -> Document:
        document = await self.repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return document

    async def search(
        self, category: str | None = None, doc_status: DocumentStatus | None = None
    ) -> list[Document]:
        return await self.repo.search(category, doc_status)

    async def get_versions(self, document_id: int) -> list[Document]:
        document = await self.get(document_id)
        if document.family_id is None:
            return [document]
        return await self.repo.get_by_family(document.family_id)

    async def get_by_entity(self, entity_type: str, entity_id: int) -> list[Document]:
        return await self.repo.get_by_entity(entity_type, entity_id)

    async def update(self, document_id: int, data: DocumentUpdate) -> Document:
        document = await self.get(document_id)
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(document, update_data)

    async def delete(self, document_id: int) -> None:
        document = await self.get(document_id)
        await self.repo.delete(document)

    async def create_version(
        self, document_id: int, data: DocumentVersionCreate
    ) -> Document:
        previous = await self.get(document_id)
        new_version = Document(
            title=data.title or previous.title,
            category=data.category or previous.category,
            entity_type=previous.entity_type,
            entity_id=previous.entity_id,
            family_id=previous.family_id,
            version=previous.version + 1,
            status=DocumentStatus.CURRENT,
            supersedes_id=previous.id,
            file_ref=data.file_ref,
            uploaded_by=data.uploaded_by,
        )
        new_version = await self.repo.create(new_version)
        await self.repo.update(previous, {"status": DocumentStatus.SUPERSEDED})
        return new_version
