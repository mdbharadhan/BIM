"""End-to-end proof of the compliance primitive: seed IS 383, evaluate a sand
delivery's measurements against it, and confirm pass/fail checks are recorded.

The delivery is attached to a Room. There is no MaterialDelivery table — that is
Squad B's scope — and the EntityRefMixin does not require the target table to
exist, so a Room stands in as the entity for now. Swap entity_type to
"material_delivery" once Squad B ships it; nothing else here changes.
"""

import pytest
from httpx import AsyncClient

from app.db.base import get_db
from app.main import app
from app.seeds.compliance import IS383_FINE_AGGREGATE, seed_standard


@pytest.fixture
async def seeded_standard(client: AsyncClient) -> dict:
    """Seed IS 383 through the same session the API is using."""
    session_gen = app.dependency_overrides.get(get_db, get_db)()
    session = await anext(session_gen)
    standard = await seed_standard(session, IS383_FINE_AGGREGATE)
    return {"id": standard.id, "code": standard.code}


@pytest.fixture
def compliant_delivery(created_room: dict, seeded_standard: dict) -> dict:
    """A sand delivery whose every measured value is inside the IS 383 limits."""
    return {
        "entity_type": "room",
        "entity_id": created_room["id"],
        "standard_id": seeded_standard["id"],
        "checked_by": "vishnu@example.com",
        "measurements": {
            "fineness_modulus": 2.6,
            "silt_content_percent": 2.1,
            "clay_lumps_percent": 0.4,
            "finer_than_75_micron_percent": 2.2,
            "chloride_content_percent": 0.01,
            "sulfate_content_percent": 0.2,
            "specific_gravity": 2.65,
            "water_absorption_percent": 1.1,
        },
        "attestations": {
            "material_test_certificate": True,
            "source_approval": True,
            "organic_impurities": True,
        },
    }


async def test_compliant_delivery_passes_every_rule(
    client: AsyncClient, compliant_delivery: dict
):
    response = await client.post("/compliance-evaluations", json=compliant_delivery)

    assert response.status_code == 201
    body = response.json()
    assert body["failed"] == 0
    assert body["passed"] == 11
    assert all(check["result"] == "pass" for check in body["checks"])


async def test_high_silt_delivery_fails_that_rule_only(
    client: AsyncClient, compliant_delivery: dict
):
    """The headline case: 6.2% silt against a 3% limit."""
    payload = {**compliant_delivery, "measurements": {**compliant_delivery["measurements"]}}
    payload["measurements"]["silt_content_percent"] = 6.2

    response = await client.post("/compliance-evaluations", json=payload)

    body = response.json()
    assert body["failed"] == 1
    failures = [c for c in body["checks"] if c["result"] == "fail"]
    assert len(failures) == 1
    assert failures[0]["measured_value"] == 6.2


async def test_checks_are_retrievable_against_the_entity(
    client: AsyncClient, compliant_delivery: dict
):
    """The recorded checks must be findable from the entity afterwards —
    otherwise the evaluation left no audit trail."""
    await client.post("/compliance-evaluations", json=compliant_delivery)

    entity_id = compliant_delivery["entity_id"]
    response = await client.get(f"/entities/room/{entity_id}/compliance-checks")

    assert response.status_code == 200
    assert len(response.json()) == 11


async def test_unmeasured_parameters_are_skipped_not_passed(
    client: AsyncClient, compliant_delivery: dict
):
    """A parameter nobody measured is a gap in the inspection, never a pass."""
    payload = {**compliant_delivery, "measurements": {"silt_content_percent": 2.1}}

    response = await client.post("/compliance-evaluations", json=payload)

    body = response.json()
    assert body["passed"] == 4  # silt + three attestations
    assert body["skipped"] > 0
    reasons = {rule["reason"] for rule in body["skipped_rules"]}
    assert "not measured" in reasons


async def test_missing_attestation_is_skipped_not_passed(
    client: AsyncClient, compliant_delivery: dict
):
    """No MTC on file must not silently pass the 'MTC provided' rule."""
    payload = {**compliant_delivery, "attestations": {}}

    response = await client.post("/compliance-evaluations", json=payload)

    body = response.json()
    skipped_names = {rule["parameter_name"] for rule in body["skipped_rules"]}
    assert "material_test_certificate" in skipped_names


async def test_failed_attestation_records_a_fail(
    client: AsyncClient, compliant_delivery: dict
):
    payload = {
        **compliant_delivery,
        "attestations": {**compliant_delivery["attestations"], "material_test_certificate": False},
    }

    response = await client.post("/compliance-evaluations", json=payload)

    body = response.json()
    assert body["failed"] == 1


async def test_unknown_standard_returns_404(client: AsyncClient, created_room: dict):
    response = await client.post(
        "/compliance-evaluations",
        json={
            "entity_type": "room",
            "entity_id": created_room["id"],
            "standard_id": 9999,
            "measurements": {},
        },
    )

    assert response.status_code == 404