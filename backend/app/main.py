from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  ensures all models register on Base.metadata
from app.api import (
    approval,
    audit,
    building,
    checklist,
    checklist_completion,
    compliance,
    document,
    floor,
    ncr,
    room,
    structural_element,
)
from app.core.config import settings
from app.db.base import Base, engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.auto_create_tables:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="BIM Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(building.router)
app.include_router(floor.router)
app.include_router(room.router)
app.include_router(structural_element.router)
app.include_router(checklist.router)
app.include_router(checklist_completion.router)
app.include_router(approval.router)
app.include_router(document.router)
app.include_router(compliance.router)
app.include_router(ncr.router)
app.include_router(audit.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "bim-backend", "status": "ok"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
