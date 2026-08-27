"""End-to-end proof of the checklist completion flow: seed Concrete Pour
Inspection, instantiate it against a Room, complete items one at a time via
the primitive's existing PATCH endpoint, and confirm derived completion
status via the new endpoint at each step."""

from httpx import AsyncClient

from app.db.base import get_db
from app.main import app
from app.seeds.checklist import CONCRETE_POUR_INSPECTION, seed_template


async def _seed_and_instantiate(client: AsyncClient, room_id: int) -> dict:
    session_gen = app.dependency_overrides.get(get_db, get_db)()
    session = await anext(session_gen)
    template = await seed_template(session, CONCRETE_POUR_INSPECTION)

    response = await client.post(
        "/checklist-instances",
        json={"template_id": template.id, "entity_type": "room", "entity_id": room_id},
    )
    return response.json()


async def test_completion_status_starts_incomplete(client: AsyncClient, created_room: dict):
    instance = await _seed_and_instantiate(client, created_room["id"])

    response = await client.get(f"/checklist-instances/{instance['id']}/completion")

    assert response.status_code == 200
    body = response.json()
    assert body["is_complete"] is False
    assert body["completed_items"] == 0
    assert len(body["pending_required_items"]) == len(instance["items"])


async def test_completion_flips_true_once_every_item_is_addressed(
    client: AsyncClient, created_room: dict
):
    instance = await _seed_and_instantiate(client, created_room["id"])

    for item in instance["items"]:
        await client.patch(
            f"/checklist-instances/{instance['id']}/items/{item['id']}",
            json={"state": "pass"},
        )

    response = await client.get(f"/checklist-instances/{instance['id']}/completion")
    body = response.json()
    assert body["is_complete"] is True
    assert body["is_fully_passed"] is True
    assert body["pending_required_items"] == []


async def test_a_failed_required_item_completes_but_does_not_fully_pass(
    client: AsyncClient, created_room: dict
):
    instance = await _seed_and_instantiate(client, created_room["id"])
    items = instance["items"]

    await client.patch(
        f"/checklist-instances/{instance['id']}/items/{items[0]['id']}",
        json={"state": "fail", "notes": "formwork not braced"},
    )
    for item in items[1:]:
        await client.patch(
            f"/checklist-instances/{instance['id']}/items/{item['id']}",
            json={"state": "pass"},
        )

    response = await client.get(f"/checklist-instances/{instance['id']}/completion")
    body = response.json()
    assert body["is_complete"] is True
    assert body["is_fully_passed"] is False
    assert items[0]["label"] in body["failed_required_items"]
