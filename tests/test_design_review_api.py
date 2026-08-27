from httpx import AsyncClient


def _review_payload(created_document: dict) -> dict:
    return {"entity_type": "document", "entity_id": created_document["id"]}


async def test_raise_design_review_defaults_to_draft(client: AsyncClient, created_document: dict):
    response = await client.post("/design-reviews", json=_review_payload(created_document))
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["entity_type"] == "document"
    assert body["review_type"] is None


async def test_submit_requires_a_valid_review_type(client: AsyncClient, created_document: dict):
    review_id = (
        await client.post("/design-reviews", json=_review_payload(created_document))
    ).json()["id"]

    response = await client.post(
        f"/design-reviews/{review_id}/submit", json={"review_type": "bogus"}
    )
    assert response.status_code == 422


async def test_full_design_review_lifecycle(client: AsyncClient, created_document: dict):
    review_id = (
        await client.post("/design-reviews", json=_review_payload(created_document))
    ).json()["id"]

    submitted = await client.post(
        f"/design-reviews/{review_id}/submit",
        json={
            "review_type": "peer_review",
            "reviewer": "lead-engineer@example.com",
            "notes": "Structural peer review of drawing rev B",
        },
    )
    assert submitted.json()["status"] == "submitted"
    assert submitted.json()["review_type"] == "peer_review"
    assert submitted.json()["notes"] == "Structural peer review of drawing rev B"

    reviewed = await client.post(
        f"/design-reviews/{review_id}/review", json={"actor": "reviewer@example.com"}
    )
    assert reviewed.json()["status"] == "under_review"
    assert reviewed.json()["current_assignee"] == "reviewer@example.com"

    approved = await client.post(
        f"/design-reviews/{review_id}/approve", json={"actor": "reviewer@example.com"}
    )
    assert approved.json()["status"] == "approved"
    assert approved.json()["review_type"] == "peer_review"

    closed = await client.post(
        f"/design-reviews/{review_id}/close", json={"actor": "qa@example.com"}
    )
    assert closed.json()["status"] == "closed"

    events = await client.get(f"/design-reviews/{review_id}/events")
    to_statuses = [e["to_status"] for e in events.json()]
    assert to_statuses == ["draft", "submitted", "under_review", "approved", "closed"]


async def test_reject_without_comment_returns_400(client: AsyncClient, created_document: dict):
    review_id = (
        await client.post("/design-reviews", json=_review_payload(created_document))
    ).json()["id"]
    await client.post(f"/design-reviews/{review_id}/submit", json={"review_type": "spec_review"})
    await client.post(f"/design-reviews/{review_id}/review", json={"actor": "reviewer@example.com"})

    response = await client.post(
        f"/design-reviews/{review_id}/reject", json={"actor": "reviewer@example.com"}
    )
    assert response.status_code == 400


async def test_resubmission_after_rejection_updates_review_type(
    client: AsyncClient, created_document: dict
):
    review_id = (
        await client.post("/design-reviews", json=_review_payload(created_document))
    ).json()["id"]
    await client.post(f"/design-reviews/{review_id}/submit", json={"review_type": "design_review"})
    await client.post(f"/design-reviews/{review_id}/review", json={"actor": "reviewer@example.com"})
    await client.post(
        f"/design-reviews/{review_id}/reject",
        json={"actor": "reviewer@example.com", "comment": "wrong scope"},
    )

    resubmitted = await client.post(
        f"/design-reviews/{review_id}/submit",
        json={"review_type": "design_change", "notes": "revised scope"},
    )
    assert resubmitted.json()["review_type"] == "design_change"
    assert resubmitted.json()["notes"] == "revised scope"


async def test_get_design_reviews_by_entity(client: AsyncClient, created_document: dict):
    payload = _review_payload(created_document)
    await client.post("/design-reviews", json=payload)

    response = await client.get(
        f"/entities/{payload['entity_type']}/{payload['entity_id']}/design-reviews"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
