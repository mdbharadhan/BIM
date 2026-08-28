"""Pure logic for encoding an audit's type into an Approval transition comment
— no database, no I/O.

Approval has no column for audit-specific metadata (only entity_type/entity_id/
status/current_assignee/timestamps), so audit_type travels inside the submit
transition's `comment` as a parseable prefix: "[audit_type=internal] <notes>".
Keeping the format/parse pair here, tested independently of the database,
means the convention is exercised the same way regardless of whether it is
called from a service test or an end-to-end API test.

This is a workaround, not the intended design — comment-encoding was chosen
over touching the Approval primitive (see docs/adr/0001-entity-reference-no-fk.md
for the same don't-modify-the-shared-primitive posture) or standing up a new
table for this one feature. It holds up only because audit metadata today is
a single small field. If audit metadata grows (more fields, values needing
their own validation/indexing, or anything queried directly rather than
read back off an Approval already in hand), the cleaner fix is a dedicated
AuditMetadata table (audit_id FK -> approvals.id, audit_type, auditor,
structured notes) instead of stretching this convention further.
"""

import enum
import re
from dataclasses import dataclass


class AuditType(enum.StrEnum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    CLIENT = "client"
    REGULATORY = "regulatory"


_PREFIX_RE = re.compile(r"^\[audit_type=(?P<type>\w+)\](?:\s+(?P<notes>.*))?$", re.DOTALL)


@dataclass(frozen=True)
class ParsedAuditSubmission:
    audit_type: AuditType | None
    notes: str | None


def format_submission_comment(audit_type: AuditType, notes: str | None) -> str:
    prefix = f"[audit_type={audit_type.value}]"
    return f"{prefix} {notes}" if notes else prefix


def parse_submission_comment(comment: str | None) -> ParsedAuditSubmission:
    """Recover the audit_type/notes encoded by format_submission_comment.

    Returns audit_type=None for a comment that predates this convention, was
    hand-edited, or carries an unrecognized type — never raises, since a
    malformed comment on old data shouldn't break reading an audit's history.
    """
    if not comment:
        return ParsedAuditSubmission(audit_type=None, notes=None)

    match = _PREFIX_RE.match(comment.strip())
    if not match:
        return ParsedAuditSubmission(audit_type=None, notes=comment)

    try:
        audit_type = AuditType(match.group("type"))
    except ValueError:
        return ParsedAuditSubmission(audit_type=None, notes=comment)

    return ParsedAuditSubmission(audit_type=audit_type, notes=match.group("notes") or None)
