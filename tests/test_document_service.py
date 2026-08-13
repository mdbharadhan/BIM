from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import DocumentStatus
from app.schemas.document import DocumentCreate, DocumentVersionCreate
from app.services.document_service import DocumentService


async def test_create_version_flips_previous_to_superseded(db_session: AsyncSession):
    service = DocumentService(db_session)
    original = await service.create(
        DocumentCreate(title="Spec", category="spec", file_ref="s3://bucket/spec-v1.pdf")
    )

    new_version = await service.create_version(
        original.id, DocumentVersionCreate(file_ref="s3://bucket/spec-v2.pdf")
    )

    refreshed_original = await service.get(original.id)
    assert refreshed_original.status == DocumentStatus.SUPERSEDED
    assert new_version.status == DocumentStatus.CURRENT
    assert new_version.family_id == original.family_id
    assert new_version.version == 2


async def test_get_versions_returns_all_versions_in_order(db_session: AsyncSession):
    service = DocumentService(db_session)
    v1 = await service.create(
        DocumentCreate(title="Spec", category="spec", file_ref="s3://bucket/spec-v1.pdf")
    )
    v2 = await service.create_version(
        v1.id, DocumentVersionCreate(file_ref="s3://bucket/spec-v2.pdf")
    )
    v3 = await service.create_version(
        v2.id, DocumentVersionCreate(file_ref="s3://bucket/spec-v3.pdf")
    )

    versions = await service.get_versions(v3.id)
    assert [v.version for v in versions] == [1, 2, 3]
