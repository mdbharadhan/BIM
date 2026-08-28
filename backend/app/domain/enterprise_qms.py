"""Category conventions and pure logic for Enterprise QMS's registers — no
database, no I/O.

Per the QA taxonomy doc, Enterprise QMS (T2 21) is "largely a consolidation
of primitives already built": CAPA and change control are Approval, document
control is Document itself, audit management is app.services.audit_service.
The one genuine gap is that risk register / compliance register / supplier
management have no home yet — each is naturally "one document, versioned
over time" (Document.category + family_id/version/status already model
"the current X" and its full history), so no new table or primitive change
is needed. RegisterCategory exists only so callers share one spelling of the
category string instead of each inventing their own — Document.category is
free text, same unenforced-vocabulary tradeoff as EntityRefMixin.entity_type
(see docs/adr/0001-entity-reference-no-fk.md).

Creating or versioning a register document goes through the existing
POST /documents and POST /documents/{id}/versions endpoints with `category`
set to one of these values — this module adds read convenience only.
"""

import enum
from datetime import datetime
from typing import Protocol


class RegisterCategory(enum.StrEnum):
    RISK_REGISTER = "risk_register"
    COMPLIANCE_REGISTER = "compliance_register"
    SUPPLIER_MANAGEMENT = "supplier_management"


class HasCreatedAt(Protocol):
    created_at: datetime


def pick_most_recent[T: HasCreatedAt](items: list[T]) -> T | None:
    """The most recently created of a set of documents sharing a category.

    Exists because a category is not a family — nothing stops two unrelated
    document families from both being marked current under the same
    category, so "the current register" is a judgment call (most recent
    wins), not a guaranteed-unique lookup.
    """
    if not items:
        return None
    return max(items, key=lambda item: item.created_at)
