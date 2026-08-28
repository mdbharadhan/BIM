from httpx import AsyncClient


async def _upload(
    client: AsyncClient, category: str, file_ref: str, title: str = "Register"
) -> dict:
    response = await client.post(
        "/documents",
        json={"title": title, "category": category, "file_ref": file_ref},
    )
    return response.json()


async def test_get_current_register_404_when_none_uploaded(client: AsyncClient):
    response = await client.get("/enterprise-qms/risk_register/current")
    assert response.status_code == 404


async def test_invalid_register_category_returns_422(client: AsyncClient):
    response = await client.get("/enterprise-qms/bogus_register/current")
    assert response.status_code == 422


async def test_get_current_register_returns_the_uploaded_document(client: AsyncClient):
    await _upload(
        client, "risk_register", "s3://bucket/risk-register.xlsx", title="Project Risk Register"
    )

    response = await client.get("/enterprise-qms/risk_register/current")
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Project Risk Register"
    assert body["category"] == "risk_register"
    assert body["status"] == "current"


async def test_new_version_is_reflected_as_current(client: AsyncClient):
    v1 = await _upload(client, "compliance_register", "s3://bucket/compliance-v1.xlsx")
    await client.post(
        f"/documents/{v1['id']}/versions",
        json={"file_ref": "s3://bucket/compliance-v2.xlsx"},
    )

    response = await client.get("/enterprise-qms/compliance_register/current")
    body = response.json()
    assert body["version"] == 2
    assert body["file_ref"] == "s3://bucket/compliance-v2.xlsx"


async def test_get_register_history_returns_the_full_family(client: AsyncClient):
    v1 = await _upload(client, "supplier_management", "s3://bucket/supplier-v1.xlsx")
    await client.post(
        f"/documents/{v1['id']}/versions",
        json={"file_ref": "s3://bucket/supplier-v2.xlsx"},
    )

    response = await client.get("/enterprise-qms/supplier_management/history")
    assert response.status_code == 200
    versions = [d["version"] for d in response.json()]
    assert versions == [1, 2]


async def test_get_register_history_is_empty_list_when_none_uploaded(client: AsyncClient):
    response = await client.get("/enterprise-qms/risk_register/history")
    assert response.status_code == 200
    assert response.json() == []
