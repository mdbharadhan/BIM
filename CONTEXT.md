# BIM Backend

Backend for tracking a building's physical structure (Buildings, Floors, Rooms, Structural
Elements) and, layered on top of it, four reusable QA/quality-assurance primitives that
construction-QA features (NCRs, audits, compliance checks, document control, ...) configure
rather than reimplement.

## Language

**Entity Reference**:
The `(entity_type, entity_id)` pair a QA primitive uses to point at any real-world thing —
a Room, a Building, or a not-yet-built table owned by another feature (a material delivery,
an NCR) — without a foreign key. `entity_type` is a lowercase snake_case singular noun
matching the target concept (`"room"`, `"structural_element"`, `"material_delivery"`).
_Avoid_: polymorphic association, generic foreign key, subject/target (pick entity).

**Checklist Template**:
A reusable, named definition of an ordered set of checklist items. Not itself attached to
anything — instances are.
_Avoid_: checklist (ambiguous between template and instance).

**Checklist Instance**:
A filled-out copy of a Checklist Template, attached via an Entity Reference to one real
thing. Its items are an immutable snapshot of the template's items at creation time — editing
the template later never changes an existing instance.
_Avoid_: checklist run, checklist submission.

**Approval**:
The current-state snapshot of a draft → submitted → under_review → approved/rejected →
closed workflow, attached via an Entity Reference. Never edited to rewrite history — see
Approval Event.
_Avoid_: sign-off, review (ambiguous with the under_review status itself).

**Approval Event**:
One append-only record of a single Approval state transition — who acted, when, and any
comment (the reason, for a rejection). The audit trail for an Approval.
_Avoid_: approval log entry, transition.

**Document**:
One version of a document. Each new version is a new Document row, not an edit to an
existing one.
_Avoid_: file, attachment.

**Document Family**:
Every version of "the same" document across its lifetime, grouped by a shared `family_id`
(not a table of its own — a grouping key on Document).
_Avoid_: document group, document set.

**Compliance Standard**:
A named code or standard (e.g. "IS 383", "LEED") that owns a set of Compliance Rules.
_Avoid_: spec, code (ambiguous with source code).

**Compliance Rule**:
A single named, checkable condition belonging to a Compliance Standard — either a numeric
threshold (e.g. silt content < 5%) or a non-numeric requirement recorded as free text (e.g.
"Material Test Certificate must be provided"). Never evaluated automatically by the
primitive itself — see Compliance Check.
_Avoid_: threshold, criterion.

**Compliance Check**:
A record of one Compliance Rule evaluated against one real thing (via an Entity Reference),
with the actual measured value and result (pass/fail/not_applicable). The result is always
set by whoever performs the check — manual today, potentially automated later — never
derived by the primitive.
_Avoid_: test result, inspection result.
