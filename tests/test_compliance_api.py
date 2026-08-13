from httpx import AsyncClient


async def test_create_standard(client: AsyncClient, compliance_standard_payload: dict):
    response = await client.post("/compliance-standards", json=compliance_standard_payload)
    assert response.status_code == 201
    assert response.json()["code"] == "IS 383"


async def test_create_rule_under_standard(
    client: AsyncClient, created_compliance_standard: dict, compliance_rule_payload: dict
):
    response = await client.post(
        f"/compliance-standards/{created_compliance_standard['id']}/rules",
        json=compliance_rule_payload,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["parameter_name"] == "silt_content_percent"
    assert body["operator"] == "lt"


async def test_create_rule_under_bogus_standard_returns_404(
    client: AsyncClient, compliance_rule_payload: dict
):
    response = await client.post("/compliance-standards/999/rules", json=compliance_rule_payload)
    assert response.status_code == 404


async def test_create_passing_check(
    client: AsyncClient, created_compliance_rule: dict, created_room: dict
):
    response = await client.post(
        "/compliance-checks",
        json={
            "rule_id": created_compliance_rule["id"],
            "entity_type": "material_delivery",
            "entity_id": created_room["id"],
            "measured_value": 3.2,
            "result": "pass",
            "checked_by": "lab@example.com",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["result"] == "pass"
    assert body["measured_value"] == 3.2


async def test_create_check_with_bogus_rule_returns_404(client: AsyncClient):
    response = await client.post(
        "/compliance-checks",
        json={
            "rule_id": 999,
            "entity_type": "material_delivery",
            "entity_id": 1,
            "result": "fail",
        },
    )
    assert response.status_code == 404


async def test_list_checks_by_rule(client: AsyncClient, created_compliance_rule: dict):
    await client.post(
        "/compliance-checks",
        json={
            "rule_id": created_compliance_rule["id"],
            "entity_type": "material_delivery",
            "entity_id": 1,
            "measured_value": 7.5,
            "result": "fail",
        },
    )
    response = await client.get(f"/compliance-rules/{created_compliance_rule['id']}/checks")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_checks_by_entity(client: AsyncClient, created_compliance_rule: dict):
    await client.post(
        "/compliance-checks",
        json={
            "rule_id": created_compliance_rule["id"],
            "entity_type": "material_delivery",
            "entity_id": 42,
            "measured_value": 2.0,
            "result": "pass",
        },
    )
    response = await client.get("/entities/material_delivery/42/compliance-checks")
    assert response.status_code == 200
    assert len(response.json()) == 1
