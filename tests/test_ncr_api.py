from httpx import AsyncClient


def _ncr_payload(created_room: dict) -> dict:
    return {"entity_type": "room", "entity_id": created_room["id"]}


async def test_raise_ncr_defaults_to_draft(client: AsyncClient, created_room: dict):
    response = await client.post("/ncrs", json=_ncr_payload(created_room))
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["entity_type"] == "room"


async def test_submit_without_comment_returns_400(client: AsyncClient, created_room: dict):
    created = (await client.post("/ncrs", json=_ncr_payload(created_room))).json()

    response = await client.post(f"/ncrs/{created['id']}/submit", json={"actor": "qa@example.com"})
    assert response.status_code == 400


async def test_full_ncr_lifecycle(client: AsyncClient, created_room: dict):
    ncr_id = (await client.post("/ncrs", json=_ncr_payload(created_room))).json()["id"]

    submitted = await client.post(
        f"/ncrs/{ncr_id}/submit",
        json={"actor": "qa@example.com", "comment": "Rebar cover deficient in Room"},
    )
    assert submitted.json()["status"] == "submitted"

    reviewed = await client.post(f"/ncrs/{ncr_id}/review", json={"actor": "reviewer@example.com"})
    assert reviewed.json()["status"] == "under_review"
    assert reviewed.json()["current_assignee"] == "reviewer@example.com"

    approved = await client.post(f"/ncrs/{ncr_id}/approve", json={"actor": "reviewer@example.com"})
    assert approved.json()["status"] == "approved"

    closed = await client.post(f"/ncrs/{ncr_id}/close", json={"actor": "qa@example.com"})
    assert closed.json()["status"] == "closed"

    events = await client.get(f"/ncrs/{ncr_id}/events")
    to_statuses = [e["to_status"] for e in events.json()]
    assert to_statuses == ["draft", "submitted", "under_review", "approved", "closed"]


async def test_reject_without_comment_returns_400(client: AsyncClient, created_room: dict):
    ncr_id = (await client.post("/ncrs", json=_ncr_payload(created_room))).json()["id"]
    await client.post(
        f"/ncrs/{ncr_id}/submit", json={"actor": "qa@example.com", "comment": "issue found"}
    )
    await client.post(f"/ncrs/{ncr_id}/review", json={"actor": "reviewer@example.com"})

    response = await client.post(f"/ncrs/{ncr_id}/reject", json={"actor": "reviewer@example.com"})
    assert response.status_code == 400


async def test_reject_with_comment_records_reason(client: AsyncClient, created_room: dict):
    ncr_id = (await client.post("/ncrs", json=_ncr_payload(created_room))).json()["id"]
    await client.post(
        f"/ncrs/{ncr_id}/submit", json={"actor": "qa@example.com", "comment": "issue found"}
    )
    await client.post(f"/ncrs/{ncr_id}/review", json={"actor": "reviewer@example.com"})

    rejected = await client.post(
        f"/ncrs/{ncr_id}/reject",
        json={"actor": "reviewer@example.com", "comment": "corrective action insufficient"},
    )
    assert rejected.json()["status"] == "rejected"


async def test_get_ncrs_by_entity(client: AsyncClient, created_room: dict):
    payload = _ncr_payload(created_room)
    await client.post("/ncrs", json=payload)

    response = await client.get(f"/entities/{payload['entity_type']}/{payload['entity_id']}/ncrs")
    assert response.status_code == 200
    assert len(response.json()) == 1
