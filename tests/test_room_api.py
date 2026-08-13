from httpx import AsyncClient


async def test_create_room(client: AsyncClient, room_payload: dict):
    response = await client.post("/rooms", json=room_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["room_name"] == room_payload["room_name"]
    assert body["floor_id"] == room_payload["floor_id"]


async def test_create_room_with_bogus_floor_returns_404(client: AsyncClient):
    response = await client.post("/rooms", json={"room_name": "Ghost", "floor_id": 999})
    assert response.status_code == 404


async def test_get_room(client: AsyncClient, created_room: dict):
    response = await client.get(f"/rooms/{created_room['id']}")
    assert response.status_code == 200


async def test_update_room(client: AsyncClient, created_room: dict):
    response = await client.put(f"/rooms/{created_room['id']}", json={"occupancy": 42})
    assert response.status_code == 200
    assert response.json()["occupancy"] == 42


async def test_delete_room(client: AsyncClient, created_room: dict):
    response = await client.delete(f"/rooms/{created_room['id']}")
    assert response.status_code == 204

    response = await client.get(f"/rooms/{created_room['id']}")
    assert response.status_code == 404


async def test_delete_room_not_found(client: AsyncClient):
    response = await client.delete("/rooms/999")
    assert response.status_code == 404


async def test_create_room_missing_required_field_returns_422(
    client: AsyncClient, created_floor: dict
):
    response = await client.post("/rooms", json={"floor_id": created_floor["id"]})
    assert response.status_code == 422


async def test_create_room_wrong_type_returns_422(client: AsyncClient, created_floor: dict):
    response = await client.post(
        "/rooms",
        json={"room_name": "Lobby", "floor_id": created_floor["id"], "occupancy": "a lot"},
    )
    assert response.status_code == 422


async def test_get_rooms_by_floor(client: AsyncClient, created_floor: dict, created_room: dict):
    response = await client.get(f"/floors/{created_floor['id']}/rooms")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == created_room["id"]
