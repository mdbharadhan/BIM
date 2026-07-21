from httpx import AsyncClient


def _element_payload(floor_id: int, room_id: int | None = None) -> dict:
    payload = {"element_name": "Ext Wall", "element_type": "wall", "floor_id": floor_id}
    if room_id is not None:
        payload["room_id"] = room_id
    return payload


async def test_create_element_without_room(client: AsyncClient, created_floor: dict):
    response = await client.post("/structural-elements", json=_element_payload(created_floor["id"]))
    assert response.status_code == 201
    assert response.json()["room_id"] is None


async def test_create_element_with_matching_room(
    client: AsyncClient, created_floor: dict, created_room: dict
):
    response = await client.post(
        "/structural-elements", json=_element_payload(created_floor["id"], created_room["id"])
    )
    assert response.status_code == 201
    assert response.json()["room_id"] == created_room["id"]


async def test_create_element_with_bogus_floor_returns_404(client: AsyncClient):
    response = await client.post("/structural-elements", json=_element_payload(999))
    assert response.status_code == 404


async def test_create_element_with_bogus_room_returns_404(client: AsyncClient, created_floor: dict):
    response = await client.post(
        "/structural-elements", json=_element_payload(created_floor["id"], 999)
    )
    assert response.status_code == 404


async def test_create_element_with_room_from_other_floor_returns_400(
    client: AsyncClient, created_building: dict, created_room: dict
):
    other_floor = (
        await client.post(
            "/floors",
            json={
                "floor_name": "Other Floor",
                "floor_number": 1,
                "building_id": created_building["id"],
            },
        )
    ).json()

    response = await client.post(
        "/structural-elements", json=_element_payload(other_floor["id"], created_room["id"])
    )
    assert response.status_code == 400


async def test_get_elements_by_room(client: AsyncClient, created_floor: dict, created_room: dict):
    created = (
        await client.post(
            "/structural-elements",
            json=_element_payload(created_floor["id"], created_room["id"]),
        )
    ).json()

    response = await client.get(f"/rooms/{created_room['id']}/elements")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == created["id"]
