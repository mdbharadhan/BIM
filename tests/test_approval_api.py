from httpx import AsyncClient


async def test_create_approval_defaults_to_draft(client: AsyncClient, approval_payload: dict):
    response = await client.post("/approvals", json=approval_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["entity_type"] == approval_payload["entity_type"]


async def test_full_approval_lifecycle(client: AsyncClient, created_approval: dict):
    approval_id = created_approval["id"]

    submitted = await client.post(
        f"/approvals/{approval_id}/submit", json={"actor": "engineer@example.com"}
    )
    assert submitted.json()["status"] == "submitted"

    reviewed = await client.post(
        f"/approvals/{approval_id}/review", json={"actor": "reviewer@example.com"}
    )
    assert reviewed.json()["status"] == "under_review"
    assert reviewed.json()["current_assignee"] == "reviewer@example.com"

    approved = await client.post(
        f"/approvals/{approval_id}/approve", json={"actor": "reviewer@example.com"}
    )
    assert approved.json()["status"] == "approved"
    assert approved.json()["current_assignee"] is None

    events = await client.get(f"/approvals/{approval_id}/events")
    to_statuses = [e["to_status"] for e in events.json()]
    assert to_statuses == ["draft", "submitted", "under_review", "approved"]


async def test_invalid_transition_returns_400(client: AsyncClient, created_approval: dict):
    response = await client.post(
        f"/approvals/{created_approval['id']}/approve", json={"actor": "reviewer@example.com"}
    )
    assert response.status_code == 400


async def test_reject_records_comment_as_reason(client: AsyncClient, created_approval: dict):
    approval_id = created_approval["id"]
    await client.post(f"/approvals/{approval_id}/submit", json={})
    await client.post(f"/approvals/{approval_id}/review", json={})

    rejected = await client.post(
        f"/approvals/{approval_id}/reject",
        json={"actor": "reviewer@example.com", "comment": "missing certification"},
    )
    assert rejected.json()["status"] == "rejected"

    events = (await client.get(f"/approvals/{approval_id}/events")).json()
    reject_event = next(e for e in events if e["to_status"] == "rejected")
    assert reject_event["comment"] == "missing certification"


async def test_get_approvals_by_entity(
    client: AsyncClient, created_approval: dict, approval_payload: dict
):
    response = await client.get(
        f"/entities/{approval_payload['entity_type']}/{approval_payload['entity_id']}/approvals"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
