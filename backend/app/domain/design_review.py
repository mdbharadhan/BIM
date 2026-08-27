"""Pure logic for encoding a design review's type into an Approval transition
comment — no database, no I/O.

Same convention as app.domain.audit, and the same workaround: Approval has no
column for review-specific metadata, so review_type travels inside the submit
transition's `comment` as a parseable prefix: "[review_type=peer_review] <notes>".
Kept as its own small module rather than sharing code with app.domain.audit —
two concrete uses doesn't yet justify a shared abstraction, and each phase's
diff stays self-contained. If a third workflow needs this same convention,
that's the point to extract a shared helper.

Covers the review/approval half of Design QA only (design reviews, peer
review, spec review, constructability review, value engineering, independent
design check, and design change management — all named as approval-primitive
uses in the QA taxonomy doc's cross-squad table). BIM coordination and clash
resolution are explicitly out of scope here — they depend on the BIM-Vision
subsystem being built separately. Drawing revision control is also excluded:
that's Document's own family_id versioning, not an approval workflow.
"""

import enum
import re
from dataclasses import dataclass


class DesignReviewType(enum.StrEnum):
    DESIGN_REVIEW = "design_review"
    PEER_REVIEW = "peer_review"
    SPEC_REVIEW = "spec_review"
    CONSTRUCTABILITY_REVIEW = "constructability_review"
    VALUE_ENGINEERING = "value_engineering"
    INDEPENDENT_DESIGN_CHECK = "independent_design_check"
    DESIGN_CHANGE = "design_change"


_PREFIX_RE = re.compile(r"^\[review_type=(?P<type>\w+)\](?:\s+(?P<notes>.*))?$", re.DOTALL)


@dataclass(frozen=True)
class ParsedReviewSubmission:
    review_type: DesignReviewType | None
    notes: str | None


def format_submission_comment(review_type: DesignReviewType, notes: str | None) -> str:
    prefix = f"[review_type={review_type.value}]"
    return f"{prefix} {notes}" if notes else prefix


def parse_submission_comment(comment: str | None) -> ParsedReviewSubmission:
    """Recover the review_type/notes encoded by format_submission_comment.

    Returns review_type=None for a comment that predates this convention, was
    hand-edited, or carries an unrecognized type — never raises, since a
    malformed comment on old data shouldn't break reading a review's history.
    """
    if not comment:
        return ParsedReviewSubmission(review_type=None, notes=None)

    match = _PREFIX_RE.match(comment.strip())
    if not match:
        return ParsedReviewSubmission(review_type=None, notes=comment)

    try:
        review_type = DesignReviewType(match.group("type"))
    except ValueError:
        return ParsedReviewSubmission(review_type=None, notes=comment)

    return ParsedReviewSubmission(review_type=review_type, notes=match.group("notes") or None)
