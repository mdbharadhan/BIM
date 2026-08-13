from httpx import AsyncClient


async def test_create_document_assigns_family_id_to_self(
    client: AsyncClient, document_payload: dict
):
    response = await client.post("/documents", json=document_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["version"] == 1
    assert body["status"] == "current"
    assert body["family_id"] == body["id"]


async def test_create_version_supersedes_previous(client: AsyncClient, created_document: dict):
    response = await client.post(
        f"/documents/{created_document['id']}/versions",
        json={"file_ref": "s3://bucket/drawing-rev-b.pdf", "uploaded_by": "jane@example.com"},
    )
    assert response.status_code == 201
    new_version = response.json()
    assert new_version["version"] == 2
    assert new_version["status"] == "current"
    assert new_version["family_id"] == created_document["family_id"]
    assert new_version["supersedes_id"] == created_document["id"]

    old = await client.get(f"/documents/{created_document['id']}")
    assert old.json()["status"] == "superseded"


async def test_get_versions_returns_full_family(client: AsyncClient, created_document: dict):
    await client.post(
        f"/documents/{created_document['id']}/versions",
        json={"file_ref": "s3://bucket/drawing-rev-b.pdf"},
    )
    response = await client.get(f"/documents/{created_document['id']}/versions")
    assert response.status_code == 200
    versions = response.json()
    assert len(versions) == 2
    assert [v["version"] for v in versions] == [1, 2]


async def test_list_documents_filtered_by_category_and_status(
    client: AsyncClient, created_document: dict
):
    response = await client.get("/documents", params={"category": "drawing", "status": "current"})
    assert response.status_code == 200
    assert any(d["id"] == created_document["id"] for d in response.json())

    response = await client.get("/documents", params={"category": "certificate"})
    assert response.json() == []


async def test_get_documents_by_entity(
    client: AsyncClient, created_document: dict, document_payload: dict
):
    response = await client.get(
        f"/entities/{document_payload['entity_type']}/{document_payload['entity_id']}/documents"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_update_document_metadata(client: AsyncClient, created_document: dict):
    response = await client.put(
        f"/documents/{created_document['id']}", json={"title": "Structural Drawing Rev A (final)"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Structural Drawing Rev A (final)"


async def test_delete_document(client: AsyncClient, created_document: dict):
    response = await client.delete(f"/documents/{created_document['id']}")
    assert response.status_code == 204

    response = await client.get(f"/documents/{created_document['id']}")
    assert response.status_code == 404
