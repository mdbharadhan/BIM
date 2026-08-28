"""Proves Asset QA's use case works through the existing Document endpoints
alone — no new API surface, matching app/domain/asset_qa.py's confirmation
that no new capability was needed.
"""

from httpx import AsyncClient

from app.domain.asset_qa import AssetDocumentCategory


async def test_asset_documents_are_created_and_found_by_category(
    client: AsyncClient, created_room: dict
):
    response = await client.post(
        "/documents",
        json={
            "title": "HVAC Unit 3 — Registration",
            "category": AssetDocumentCategory.REGISTRATION.value,
            "entity_type": "room",
            "entity_id": created_room["id"],
            "file_ref": "s3://bucket/hvac-unit-3-registration.pdf",
        },
    )
    assert response.status_code == 201

    listed = await client.get(f"/documents?category={AssetDocumentCategory.REGISTRATION.value}")
    assert len(listed.json()) == 1
    assert listed.json()[0]["title"] == "HVAC Unit 3 — Registration"


async def test_asset_warranty_renewal_is_a_new_version_not_a_new_record(
    client: AsyncClient, created_room: dict
):
    v1 = await client.post(
        "/documents",
        json={
            "title": "HVAC Unit 3 — Warranty",
            "category": AssetDocumentCategory.WARRANTY.value,
            "entity_type": "room",
            "entity_id": created_room["id"],
            "file_ref": "s3://bucket/hvac-unit-3-warranty-v1.pdf",
        },
    )
    document_id = v1.json()["id"]

    v2 = await client.post(
        f"/documents/{document_id}/versions",
        json={"file_ref": "s3://bucket/hvac-unit-3-warranty-extended.pdf"},
    )
    assert v2.json()["version"] == 2
    assert v2.json()["status"] == "current"

    versions = await client.get(f"/documents/{document_id}/versions")
    assert [d["version"] for d in versions.json()] == [1, 2]
    assert versions.json()[0]["status"] == "superseded"


async def test_all_documents_for_an_asset_are_found_via_entity_lookup(
    client: AsyncClient, created_room: dict
):
    for category in (
        AssetDocumentCategory.REGISTRATION,
        AssetDocumentCategory.LIFECYCLE_RECORD,
        AssetDocumentCategory.MAINTENANCE_PLAN,
    ):
        await client.post(
            "/documents",
            json={
                "title": f"Elevator A — {category.value}",
                "category": category.value,
                "entity_type": "room",
                "entity_id": created_room["id"],
                "file_ref": f"s3://bucket/elevator-a-{category.value}.pdf",
            },
        )

    response = await client.get(f"/entities/room/{created_room['id']}/documents")
    assert len(response.json()) == 3
