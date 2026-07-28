from httpx import AsyncClient


async def test_create_floor(client: AsyncClient, floor_payload: dict):
    response = await client.post("/floors", json=floor_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["floor_name"] == floor_payload["floor_name"]
    assert body["building_id"] == floor_payload["building_id"]


async def test_create_floor_with_bogus_building_returns_404(client: AsyncClient):
    response = await client.post(
        "/floors", json={"floor_name": "Ghost", "floor_number": 1, "building_id": 999}
    )
    assert response.status_code == 404


async def test_get_floor(client: AsyncClient, created_floor: dict):
    response = await client.get(f"/floors/{created_floor['id']}")
    assert response.status_code == 200


async def test_update_floor(client: AsyncClient, created_floor: dict):
    response = await client.put(f"/floors/{created_floor['id']}", json={"floor_number": 5})
    assert response.status_code == 200
    assert response.json()["floor_number"] == 5


async def test_delete_floor(client: AsyncClient, created_floor: dict):
    response = await client.delete(f"/floors/{created_floor['id']}")
    assert response.status_code == 204

    response = await client.get(f"/floors/{created_floor['id']}")
    assert response.status_code == 404


async def test_delete_floor_not_found(client: AsyncClient):
    response = await client.delete("/floors/999")
    assert response.status_code == 404


async def test_create_floor_missing_required_field_returns_422(
    client: AsyncClient, created_building: dict
):
    response = await client.post(
        "/floors", json={"floor_number": 1, "building_id": created_building["id"]}
    )
    assert response.status_code == 422


async def test_create_floor_wrong_type_returns_422(client: AsyncClient, created_building: dict):
    response = await client.post(
        "/floors",
        json={
            "floor_name": "Ground",
            "floor_number": "not-a-number",
            "building_id": created_building["id"],
        },
    )
    assert response.status_code == 422


async def test_get_floors_by_building(
    client: AsyncClient, created_building: dict, created_floor: dict
):
    response = await client.get(f"/buildings/{created_building['id']}/floors")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == created_floor["id"]


async def test_get_floors_by_building_empty_for_new_building(
    client: AsyncClient, building_payload: dict
):
    other_building = (await client.post("/buildings", json=building_payload)).json()
    response = await client.get(f"/buildings/{other_building['id']}/floors")
    assert response.status_code == 200
    assert response.json() == []
