from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base, enable_sqlite_foreign_keys, get_db
from app.main import app


@pytest.fixture
async def test_engine() -> AsyncGenerator:
    # In-memory sqlite is per-connection: StaticPool keeps one connection alive
    # for the whole test, otherwise each new connection sees a blank DB.
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    enable_sqlite_foreign_keys(engine)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
def session_factory(test_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture
async def db_session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def building_payload() -> dict:
    return {"name": "Tower A", "address": "123 Main St"}


@pytest.fixture
async def created_building(client: AsyncClient, building_payload: dict) -> dict:
    response = await client.post("/buildings", json=building_payload)
    return response.json()


@pytest.fixture
def floor_payload(created_building: dict) -> dict:
    return {
        "floor_name": "Ground Floor",
        "floor_number": 0,
        "building_id": created_building["id"],
    }


@pytest.fixture
async def created_floor(client: AsyncClient, floor_payload: dict) -> dict:
    response = await client.post("/floors", json=floor_payload)
    return response.json()


@pytest.fixture
def room_payload(created_floor: dict) -> dict:
    return {
        "room_name": "Lobby",
        "room_number": "G-01",
        "room_type": "lobby",
        "floor_id": created_floor["id"],
        "area": 50.0,
        "occupancy": 20,
    }


@pytest.fixture
async def created_room(client: AsyncClient, room_payload: dict) -> dict:
    response = await client.post("/rooms", json=room_payload)
    return response.json()


@pytest.fixture
def checklist_template_payload() -> dict:
    return {
        "name": "Concrete Pour Checklist",
        "description": "Pre-pour verification",
        "items": [
            {"label": "Formwork inspected", "sequence": 0, "is_required": True},
            {"label": "Rebar cover verified", "sequence": 1, "is_required": True},
        ],
    }


@pytest.fixture
async def created_checklist_template(
    client: AsyncClient, checklist_template_payload: dict
) -> dict:
    response = await client.post("/checklist-templates", json=checklist_template_payload)
    return response.json()


@pytest.fixture
def approval_payload(created_room: dict) -> dict:
    return {"entity_type": "room", "entity_id": created_room["id"]}


@pytest.fixture
async def created_approval(client: AsyncClient, approval_payload: dict) -> dict:
    response = await client.post("/approvals", json=approval_payload)
    return response.json()


@pytest.fixture
def document_payload(created_room: dict) -> dict:
    return {
        "title": "Structural Drawing Rev A",
        "category": "drawing",
        "entity_type": "room",
        "entity_id": created_room["id"],
        "file_ref": "s3://bucket/drawing-rev-a.pdf",
        "uploaded_by": "jane@example.com",
    }


@pytest.fixture
async def created_document(client: AsyncClient, document_payload: dict) -> dict:
    response = await client.post("/documents", json=document_payload)
    return response.json()


@pytest.fixture
def compliance_standard_payload() -> dict:
    return {"code": "IS 383", "name": "Specification for Coarse and Fine Aggregates"}


@pytest.fixture
async def created_compliance_standard(
    client: AsyncClient, compliance_standard_payload: dict
) -> dict:
    response = await client.post("/compliance-standards", json=compliance_standard_payload)
    return response.json()


@pytest.fixture
def compliance_rule_payload() -> dict:
    return {
        "name": "Silt content max",
        "parameter_name": "silt_content_percent",
        "operator": "lt",
        "threshold_value": 5,
        "unit": "%",
    }


@pytest.fixture
async def created_compliance_rule(
    client: AsyncClient, created_compliance_standard: dict, compliance_rule_payload: dict
) -> dict:
    response = await client.post(
        f"/compliance-standards/{created_compliance_standard['id']}/rules",
        json=compliance_rule_payload,
    )
    return response.json()
