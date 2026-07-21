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
