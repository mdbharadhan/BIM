"""Contract QA — configuring two existing primitives, not new code.

Contract documents (the contract itself, BOQ, variation orders, payment
milestone certificates, claims) are Document Register entries under the
categories below.

Contract-clause compliance uses the Compliance primitive exactly as it
already works, with no code changes: POST /compliance-standards to create a
standard representing one specific contract, POST
/compliance-standards/{id}/rules for its individual clauses, then record
checks against whatever entity the clause concerns. Unlike IS 383 or LEED
(app/seeds/compliance.py), no contract-clause standard is seeded here — a
contract's clauses are project-specific, not a reusable public standard, and
seeding a fabricated one would be inventing data with nothing real behind
it. tests/test_contract_qa.py exercises this path end-to-end (via the
existing API) to prove it works, without adding anything to ALL_STANDARDS.

Variation tracking, claims support, and payment milestone verification are
each "a document, optionally followed by an Approval sign-off" — the
sign-off half is the same Approval primitive already used for NCR, Audit,
and Design Review, so a caller wanting sign-off on a variation order raises
an Approval against entity_type="document"/entity_id=<the variation order's
Document row>, exactly as Design QA does. No new workflow code needed.
"""

import enum


class ContractDocumentCategory(enum.StrEnum):
    CONTRACT = "contract"
    BOQ = "boq"
    VARIATION_ORDER = "variation_order"
    PAYMENT_MILESTONE_CERTIFICATE = "payment_milestone_certificate"
    CLAIM = "claim"
