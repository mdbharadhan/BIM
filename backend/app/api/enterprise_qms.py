from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.domain.enterprise_qms import RegisterCategory
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.enterprise_qms_service import EnterpriseQmsService

router = APIRouter(tags=["Enterprise QMS"])


@router.get("/enterprise-qms/{register}/current", response_model=DocumentResponse)
async def get_current_register(
    register: RegisterCategory, db: AsyncSession = Depends(get_db)
) -> Document:
    return await EnterpriseQmsService(db).get_current(register)


@router.get("/enterprise-qms/{register}/history", response_model=list[DocumentResponse])
async def get_register_history(
    register: RegisterCategory, db: AsyncSession = Depends(get_db)
) -> list[Document]:
    return await EnterpriseQmsService(db).get_history(register)
