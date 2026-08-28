import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enterprise_qms import RegisterCategory
from app.schemas.document import DocumentCreate, DocumentVersionCreate
from app.services.document_service import DocumentService
from app.services.enterprise_qms_service import EnterpriseQmsService


async def test_get_current_or_none_with_no_documents_is_none(db_session: AsyncSession):
    service = EnterpriseQmsService(db_session)
    assert await service.get_current_or_none(RegisterCategory.RISK_REGISTER) is None


async def test_get_current_raises_404_when_none_exists(db_session: AsyncSession):
    service = EnterpriseQmsService(db_session)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_current(RegisterCategory.COMPLIANCE_REGISTER)
    assert exc_info.value.status_code == 404


async def test_get_current_returns_the_uploaded_register(db_session: AsyncSession):
    documents = DocumentService(db_session)
    await documents.create(
        DocumentCreate(
            title="Q1 Risk Register",
            category=RegisterCategory.RISK_REGISTER.value,
            file_ref="s3://bucket/risk-register-q1.xlsx",
            uploaded_by="qms@example.com",
        )
    )

    service = EnterpriseQmsService(db_session)
    current = await service.get_current(RegisterCategory.RISK_REGISTER)
    assert current.title == "Q1 Risk Register"


async def test_get_current_ignores_other_categories(db_session: AsyncSession):
    documents = DocumentService(db_session)
    await documents.create(
        DocumentCreate(
            title="Some Drawing",
            category="drawing",
            file_ref="s3://bucket/drawing.pdf",
        )
    )

    service = EnterpriseQmsService(db_session)
    assert await service.get_current_or_none(RegisterCategory.RISK_REGISTER) is None


async def test_new_version_becomes_current_and_supersedes_the_old_one(db_session: AsyncSession):
    documents = DocumentService(db_session)
    v1 = await documents.create(
        DocumentCreate(
            title="Supplier Management Log",
            category=RegisterCategory.SUPPLIER_MANAGEMENT.value,
            file_ref="s3://bucket/supplier-log-v1.xlsx",
        )
    )
    await documents.create_version(
        v1.id,
        DocumentVersionCreate(file_ref="s3://bucket/supplier-log-v2.xlsx"),
    )

    service = EnterpriseQmsService(db_session)
    current = await service.get_current(RegisterCategory.SUPPLIER_MANAGEMENT)
    assert current.file_ref == "s3://bucket/supplier-log-v2.xlsx"
    assert current.version == 2


async def test_get_history_returns_the_full_family_oldest_first(db_session: AsyncSession):
    documents = DocumentService(db_session)
    v1 = await documents.create(
        DocumentCreate(
            title="Compliance Register",
            category=RegisterCategory.COMPLIANCE_REGISTER.value,
            file_ref="s3://bucket/compliance-register-v1.xlsx",
        )
    )
    v2 = await documents.create_version(
        v1.id, DocumentVersionCreate(file_ref="s3://bucket/compliance-register-v2.xlsx")
    )
    await documents.create_version(
        v2.id, DocumentVersionCreate(file_ref="s3://bucket/compliance-register-v3.xlsx")
    )

    service = EnterpriseQmsService(db_session)
    history = await service.get_history(RegisterCategory.COMPLIANCE_REGISTER)
    assert [d.version for d in history] == [1, 2, 3]


async def test_get_history_with_no_documents_is_empty(db_session: AsyncSession):
    service = EnterpriseQmsService(db_session)
    assert await service.get_history(RegisterCategory.SUPPLIER_MANAGEMENT) == []
