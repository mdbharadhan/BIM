"""Proves Contract QA's use case works through existing endpoints alone,
matching app/domain/contract_qa.py's confirmation that no new capability
was needed: Document for contract documents, Compliance for clause
compliance (created ad hoc here, never added to app/seeds/compliance.py's
ALL_STANDARDS — see that module's docstring for why), and Approval for
sign-off on a document, exactly as Design QA uses it.
"""

from httpx import AsyncClient

from app.domain.contract_qa import ContractDocumentCategory


async def test_contract_documents_are_created_and_found_by_category(client: AsyncClient):
    response = await client.post(
        "/documents",
        json={
            "title": "Main Contract Agreement",
            "category": ContractDocumentCategory.CONTRACT.value,
            "file_ref": "s3://bucket/main-contract.pdf",
        },
    )
    assert response.status_code == 201

    listed = await client.get(f"/documents?category={ContractDocumentCategory.CONTRACT.value}")
    assert len(listed.json()) == 1


async def test_clause_compliance_is_an_ad_hoc_standard_not_a_seeded_one(client: AsyncClient):
    """Illustrative only: this standard exists for the duration of the test,
    the same way any real project would create their own contract's clause
    standard through this same API — it is never added to
    app/seeds/compliance.py's ALL_STANDARDS."""
    standard = await client.post(
        "/compliance-standards",
        json={
            "code": "CONTRACT-TEST-001",
            "name": "Illustrative Contract — Clause Compliance (test fixture, not a real contract)",
        },
    )
    assert standard.status_code == 201
    standard_id = standard.json()["id"]

    rule = await client.post(
        f"/compliance-standards/{standard_id}/rules",
        json={
            "name": "Retention held at contractually agreed percentage",
            "operator": "lte",
            "parameter_name": "retention_percent",
            "threshold_value": 5.0,
            "unit": "%",
        },
    )
    assert rule.status_code == 201
    rule_id = rule.json()["id"]

    milestone_certificate = await client.post(
        "/documents",
        json={
            "title": "Payment Milestone 4 Certificate",
            "category": ContractDocumentCategory.PAYMENT_MILESTONE_CERTIFICATE.value,
            "file_ref": "s3://bucket/milestone-4-cert.pdf",
        },
    )
    document_id = milestone_certificate.json()["id"]

    check = await client.post(
        "/compliance-checks",
        json={
            "entity_type": "document",
            "entity_id": document_id,
            "rule_id": rule_id,
            "measured_value": 5.0,
            "result": "pass",
            "checked_by": "contracts@example.com",
        },
    )
    assert check.status_code == 201
    assert check.json()["result"] == "pass"


async def test_variation_order_can_be_signed_off_via_approval(client: AsyncClient):
    variation_order = await client.post(
        "/documents",
        json={
            "title": "Variation Order 3 — Additional Waterproofing",
            "category": ContractDocumentCategory.VARIATION_ORDER.value,
            "file_ref": "s3://bucket/vo-3.pdf",
        },
    )
    document_id = variation_order.json()["id"]

    approval = await client.post(
        "/approvals", json={"entity_type": "document", "entity_id": document_id}
    )
    assert approval.status_code == 201
    assert approval.json()["status"] == "draft"
