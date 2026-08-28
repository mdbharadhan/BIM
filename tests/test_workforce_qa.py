"""Proves Workforce QA's use case works through the existing Document
endpoints alone — no new API surface, matching
app/domain/workforce_qa.py's confirmation that no new capability was
needed. CERTIFICATE reuses the existing "certificate" convention already
documented for Material QA (docs/primitives/document.md).
"""

from httpx import AsyncClient

from app.domain.workforce_qa import WorkforceDocumentCategory


async def test_certification_is_project_global_and_identifies_the_person_by_title(
    client: AsyncClient,
):
    response = await client.post(
        "/documents",
        json={
            "title": "Jane Doe — NDT Level II Certification",
            "category": WorkforceDocumentCategory.CERTIFICATE.value,
            "file_ref": "s3://bucket/jane-doe-ndt-l2.pdf",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["entity_type"] is None
    assert body["category"] == "certificate"


async def test_recertification_is_a_new_version_not_a_new_record(client: AsyncClient):
    v1 = await client.post(
        "/documents",
        json={
            "title": "Jane Doe — NDT Level II Certification",
            "category": WorkforceDocumentCategory.CERTIFICATE.value,
            "file_ref": "s3://bucket/jane-doe-ndt-l2-2024.pdf",
        },
    )
    document_id = v1.json()["id"]

    v2 = await client.post(
        f"/documents/{document_id}/versions",
        json={"file_ref": "s3://bucket/jane-doe-ndt-l2-2026.pdf"},
    )
    assert v2.json()["version"] == 2

    versions = await client.get(f"/documents/{document_id}/versions")
    assert len(versions.json()) == 2


async def test_training_records_are_filterable_by_category(client: AsyncClient):
    await client.post(
        "/documents",
        json={
            "title": "Jane Doe — Confined Space Entry Training",
            "category": WorkforceDocumentCategory.TRAINING_RECORD.value,
            "file_ref": "s3://bucket/jane-doe-confined-space.pdf",
        },
    )

    response = await client.get(
        f"/documents?category={WorkforceDocumentCategory.TRAINING_RECORD.value}"
    )
    assert len(response.json()) == 1
