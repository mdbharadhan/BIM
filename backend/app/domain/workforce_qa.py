"""Category conventions for Workforce QA — no database, no I/O.

Inspector qualification and engineer certification are already documented
as a Document Register use case (docs/primitives/document.md's own example:
"an inspector's certification document (category='certificate') —
re-certification is a new version, not a new record"). CERTIFICATE below
names that existing convention rather than inventing a new one — the same
category value Material QA already uses for a Material Test Certificate.
Training records and competency assessments follow the identical shape.

There's no Person/Worker primitive table to attach these to (out of scope
here), so entity_type/entity_id are left unset; the document's title
carries whose record it is (e.g. "Jane Doe — NDT Level II Certification"),
same as any project-global document.

Skill matrix and authorization tracking (T2 §18) are cross-person rollups of
these records, not documents themselves — a queryable "skill matrix" view
is future feature-layer work once there's enough real certification data to
roll up, not part of this phase.
"""

import enum


class WorkforceDocumentCategory(enum.StrEnum):
    CERTIFICATE = "certificate"
    TRAINING_RECORD = "training_record"
    COMPETENCY_ASSESSMENT = "competency_assessment"
