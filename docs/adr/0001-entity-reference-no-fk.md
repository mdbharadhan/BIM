# Entity Reference uses no foreign key

**Status**: accepted

Checklist, Approval, Document, and Compliance Check all need to attach to "some real-world
thing," but that thing is frequently owned by a feature or squad that hasn't built its table
yet (an NCR, a material delivery, a procurement request). We decided to attach via a plain
`entity_type: str` + `entity_id: int` pair with a composite index and **no foreign key
constraint**, rather than a real FK per relationship or a single-table-inheritance scheme.

## Considered options

- **A real FK per use case** (e.g. `room_id` on `ChecklistInstance`) — rejected: would
  require a new column, migration, and repository method on every primitive for every new
  entity type, defeating the point of a shared primitive.
- **Single-table inheritance / a universal `entities` table other tables join into** —
  rejected: forces every domain table (Room, Building, and every future one) to be rewritten
  to inherit from it; far too invasive for existing and future squads to adopt.

## Consequences

- No referential integrity: deleting a Room, Building, etc. silently orphans any attached
  QA records (no CASCADE/SET NULL is possible without a real FK). Accepted deliberately —
  QA/audit history often needs to outlive the thing it was about.
- `entity_id` assumes an integer primary key on every attachable table — true everywhere in
  this repo today, but an implicit contract on any future table.
- `entity_type` has no enforced vocabulary; correctness relies on the naming convention in
  `CONTEXT.md` (lowercase snake_case singular), not the database. A typo (`"rooms"` vs
  `"room"`) is caught by nothing at the DB layer.
