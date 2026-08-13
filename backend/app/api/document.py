from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.domain.enums import DocumentStatus
from app.models.document import Document
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    DocumentVersionCreate,
)
from app.services.document_service import DocumentService

router = APIRouter(tags=["Documents"])


@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    data: DocumentCreate, db: AsyncSession = Depends(get_db)
) -> Document:
    return await DocumentService(db).create(data)


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    category: str | None = Query(default=None),
    doc_status: DocumentStatus | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
) -> list[Document]:
    return await DocumentService(db).search(category, doc_status)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)) -> Document:
    return await DocumentService(db).get(document_id)


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int, data: DocumentUpdate, db: AsyncSession = Depends(get_db)
) -> Document:
    return await DocumentService(db).update(document_id, data)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)) -> None:
    await DocumentService(db).delete(document_id)


@router.post("/documents/{document_id}/versions", response_model=DocumentResponse, status_code=201)
async def create_document_version(
    document_id: int, data: DocumentVersionCreate, db: AsyncSession = Depends(get_db)
) -> Document:
    return await DocumentService(db).create_version(document_id, data)


@router.get("/documents/{document_id}/versions", response_model=list[DocumentResponse])
async def list_document_versions(
    document_id: int, db: AsyncSession = Depends(get_db)
) -> list[Document]:
    return await DocumentService(db).get_versions(document_id)


@router.get("/entities/{entity_type}/{entity_id}/documents", response_model=list[DocumentResponse])
async def get_documents_by_entity(
    entity_type: str, entity_id: int, db: AsyncSession = Depends(get_db)
) -> list[Document]:
    return await DocumentService(db).get_by_entity(entity_type, entity_id)
