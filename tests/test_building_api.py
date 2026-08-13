from httpx import AsyncClient


async def test_create_building(client: AsyncClient, building_payload: dict):
    response = await client.post("/buildings", json=building_payload)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == building_payload["name"]
    assert body["id"] is not None


async def test_list_buildings(client: AsyncClient, created_building: dict):
    response = await client.get("/buildings")
    assert response.status_code == 200
    assert any(b["id"] == created_building["id"] for b in response.json())


async def test_get_building(client: AsyncClient, created_building: dict):
    response = await client.get(f"/buildings/{created_building['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created_building["id"]


async def test_get_building_not_found(client: AsyncClient):
    response = await client.get("/buildings/999")
    assert response.status_code == 404


async def test_update_building(client: AsyncClient, created_building: dict):
    response = await client.put(
        f"/buildings/{created_building['id']}", json={"name": "Renamed Tower"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed Tower"


async def test_delete_building(client: AsyncClient, created_building: dict):
    response = await client.delete(f"/buildings/{created_building['id']}")
    assert response.status_code == 204

    response = await client.get(f"/buildings/{created_building['id']}")
    assert response.status_code == 404
