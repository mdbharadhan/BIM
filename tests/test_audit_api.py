from httpx import AsyncClient


def _audit_payload(created_room: dict) -> dict:
    return {"entity_type": "room", "entity_id": created_room["id"]}


async def test_raise_audit_defaults_to_draft(client: AsyncClient, created_room: dict):
    response = await client.post("/audits", json=_audit_payload(created_room))
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["audit_type"] is None


async def test_submit_requires_a_valid_audit_type(client: AsyncClient, created_room: dict):
    audit_id = (await client.post("/audits", json=_audit_payload(created_room))).json()["id"]

    response = await client.post(f"/audits/{audit_id}/submit", json={"audit_type": "bogus"})
    assert response.status_code == 422


async def test_full_audit_lifecycle(client: AsyncClient, created_room: dict):
    audit_id = (await client.post("/audits", json=_audit_payload(created_room))).json()["id"]

    submitted = await client.post(
        f"/audits/{audit_id}/submit",
        json={
            "audit_type": "regulatory",
            "auditor": "inspector@example.com",
            "notes": "Fire safety spot-check",
        },
    )
    assert submitted.json()["status"] == "submitted"
    assert submitted.json()["audit_type"] == "regulatory"
    assert submitted.json()["notes"] == "Fire safety spot-check"

    reviewed = await client.post(
        f"/audits/{audit_id}/review", json={"actor": "reviewer@example.com"}
    )
    assert reviewed.json()["status"] == "under_review"
    assert reviewed.json()["current_assignee"] == "reviewer@example.com"

    approved = await client.post(
        f"/audits/{audit_id}/approve", json={"actor": "reviewer@example.com"}
    )
    assert approved.json()["status"] == "approved"
    assert approved.json()["audit_type"] == "regulatory"

    closed = await client.post(f"/audits/{audit_id}/close", json={"actor": "qa@example.com"})
    assert closed.json()["status"] == "closed"

    events = await client.get(f"/audits/{audit_id}/events")
    to_statuses = [e["to_status"] for e in events.json()]
    assert to_statuses == ["draft", "submitted", "under_review", "approved", "closed"]


async def test_reject_without_comment_returns_400(client: AsyncClient, created_room: dict):
    audit_id = (await client.post("/audits", json=_audit_payload(created_room))).json()["id"]
    await client.post(f"/audits/{audit_id}/submit", json={"audit_type": "internal"})
    await client.post(f"/audits/{audit_id}/review", json={"actor": "reviewer@example.com"})

    response = await client.post(
        f"/audits/{audit_id}/reject", json={"actor": "reviewer@example.com"}
    )
    assert response.status_code == 400


async def test_resubmission_after_rejection_updates_audit_type(
    client: AsyncClient, created_room: dict
):
    audit_id = (await client.post("/audits", json=_audit_payload(created_room))).json()["id"]
    await client.post(f"/audits/{audit_id}/submit", json={"audit_type": "internal"})
    await client.post(f"/audits/{audit_id}/review", json={"actor": "reviewer@example.com"})
    await client.post(
        f"/audits/{audit_id}/reject",
        json={"actor": "reviewer@example.com", "comment": "wrong scope"},
    )

    resubmitted = await client.post(
        f"/audits/{audit_id}/submit", json={"audit_type": "external", "notes": "corrected scope"}
    )
    assert resubmitted.json()["audit_type"] == "external"
    assert resubmitted.json()["notes"] == "corrected scope"


async def test_get_audits_by_entity(client: AsyncClient, created_room: dict):
    payload = _audit_payload(created_room)
    await client.post("/audits", json=payload)

    response = await client.get(f"/entities/{payload['entity_type']}/{payload['entity_id']}/audits")
    assert response.status_code == 200
    assert len(response.json()) == 1
