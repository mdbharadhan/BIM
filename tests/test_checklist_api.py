from httpx import AsyncClient


async def test_create_template_with_items(client: AsyncClient, checklist_template_payload: dict):
    response = await client.post("/checklist-templates", json=checklist_template_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == checklist_template_payload["name"]
    assert len(body["items"]) == 2
    assert body["items"][0]["label"] == "Formwork inspected"


async def test_get_template(client: AsyncClient, created_checklist_template: dict):
    response = await client.get(f"/checklist-templates/{created_checklist_template['id']}")
    assert response.status_code == 200


async def test_get_template_not_found(client: AsyncClient):
    response = await client.get("/checklist-templates/999")
    assert response.status_code == 404


async def test_update_template(client: AsyncClient, created_checklist_template: dict):
    response = await client.put(
        f"/checklist-templates/{created_checklist_template['id']}",
        json={"name": "Revised Pour Checklist"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Revised Pour Checklist"


async def test_add_and_delete_template_item(client: AsyncClient, created_checklist_template: dict):
    template_id = created_checklist_template["id"]
    response = await client.post(
        f"/checklist-templates/{template_id}/items",
        json={"label": "Curing plan confirmed", "sequence": 2},
    )
    assert response.status_code == 201
    item_id = response.json()["id"]

    delete_response = await client.delete(f"/checklist-templates/{template_id}/items/{item_id}")
    assert delete_response.status_code == 204


async def test_delete_template(client: AsyncClient, created_checklist_template: dict):
    response = await client.delete(f"/checklist-templates/{created_checklist_template['id']}")
    assert response.status_code == 204


async def test_create_instance_snapshots_template_items(
    client: AsyncClient, created_checklist_template: dict, created_room: dict
):
    response = await client.post(
        "/checklist-instances",
        json={
            "template_id": created_checklist_template["id"],
            "entity_type": "room",
            "entity_id": created_room["id"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "not_started"
    assert len(body["items"]) == 2
    assert body["items"][0]["label"] == "Formwork inspected"
    assert body["items"][0]["state"] == "pending"


async def test_create_instance_with_bogus_template_returns_404(
    client: AsyncClient, created_room: dict
):
    response = await client.post(
        "/checklist-instances",
        json={"template_id": 999, "entity_type": "room", "entity_id": created_room["id"]},
    )
    assert response.status_code == 404


async def test_editing_template_does_not_change_existing_instance(
    client: AsyncClient, created_checklist_template: dict, created_room: dict
):
    instance_response = await client.post(
        "/checklist-instances",
        json={
            "template_id": created_checklist_template["id"],
            "entity_type": "room",
            "entity_id": created_room["id"],
        },
    )
    instance = instance_response.json()
    item_id = created_checklist_template["items"][0]["id"]

    await client.delete(f"/checklist-templates/{created_checklist_template['id']}/items/{item_id}")

    refreshed = await client.get(f"/checklist-instances/{instance['id']}")
    assert len(refreshed.json()["items"]) == 2


async def test_complete_item_updates_instance_status(
    client: AsyncClient, created_checklist_template: dict, created_room: dict
):
    instance = (
        await client.post(
            "/checklist-instances",
            json={
                "template_id": created_checklist_template["id"],
                "entity_type": "room",
                "entity_id": created_room["id"],
            },
        )
    ).json()
    items = instance["items"]

    first = await client.patch(
        f"/checklist-instances/{instance['id']}/items/{items[0]['id']}",
        json={"state": "pass", "completed_by": "inspector@example.com"},
    )
    assert first.status_code == 200
    assert first.json()["status"] == "in_progress"

    second = await client.patch(
        f"/checklist-instances/{instance['id']}/items/{items[1]['id']}",
        json={"state": "fail", "notes": "cover too shallow"},
    )
    assert second.json()["status"] == "completed"
    completed_item = next(i for i in second.json()["items"] if i["id"] == items[1]["id"])
    assert completed_item["state"] == "fail"
    assert completed_item["notes"] == "cover too shallow"
    assert completed_item["completed_at"] is not None


async def test_complete_item_not_found(client: AsyncClient, created_checklist_template: dict):
    instance = (
        await client.post(
            "/checklist-instances",
            json={
                "template_id": created_checklist_template["id"],
                "entity_type": "room",
                "entity_id": 1,
            },
        )
    ).json()
    response = await client.patch(
        f"/checklist-instances/{instance['id']}/items/999", json={"state": "pass"}
    )
    assert response.status_code == 404


async def test_get_instances_by_entity(
    client: AsyncClient, created_checklist_template: dict, created_room: dict
):
    await client.post(
        "/checklist-instances",
        json={
            "template_id": created_checklist_template["id"],
            "entity_type": "room",
            "entity_id": created_room["id"],
        },
    )
    response = await client.get(f"/entities/room/{created_room['id']}/checklist-instances")
    assert response.status_code == 200
    assert len(response.json()) == 1
