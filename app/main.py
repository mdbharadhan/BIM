from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  ensures all models register on Base.metadata
from app.api import building, floor, room, structural_element
from app.core.config import settings
from app.db.base import Base, engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.auto_create_tables:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="BIM Backend", lifespan=lifespan)

app.include_router(building.router)
app.include_router(floor.router)
app.include_router(room.router)
app.include_router(structural_element.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "bim-backend", "status": "ok"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
