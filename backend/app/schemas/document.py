from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import DocumentStatus


class DocumentCreate(BaseModel):
    title: str
    category: str
    entity_type: str | None = None
    entity_id: int | None = None
    file_ref: str
    uploaded_by: str | None = None
    status: DocumentStatus = DocumentStatus.CURRENT


class DocumentUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    entity_type: str | None = None
    entity_id: int | None = None
    status: DocumentStatus | None = None


class DocumentVersionCreate(BaseModel):
    file_ref: str
    uploaded_by: str | None = None
    title: str | None = None
    category: str | None = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    category: str
    entity_type: str | None
    entity_id: int | None
    family_id: int | None
    version: int
    status: DocumentStatus
    supersedes_id: int | None
    file_ref: str
    uploaded_by: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
