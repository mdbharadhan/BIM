# Approval

A generic `draft → submitted → under_review → approved/rejected → closed` sign-off state
machine, attached to any real-world thing. Every transition is logged as an append-only
**event** (actor, timestamp, comment) — the `Approval` row itself only ever shows the
current state; the full history lives in its events.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/approvals` | Create a draft approval on `entity_type`/`entity_id` |
| GET | `/approvals` | List approvals |
| GET | `/approvals/{id}` | Read current state |
| GET | `/approvals/{id}/events` | Full transition history (who, when, comment) |
| POST | `/approvals/{id}/submit` | draft → submitted |
| POST | `/approvals/{id}/review` | submitted → under_review (sets `current_assignee`) |
| POST | `/approvals/{id}/approve` | under_review → approved |
| POST | `/approvals/{id}/reject` | under_review → rejected (comment = reason) |
| POST | `/approvals/{id}/close` | approved → closed |
| GET | `/entities/{entity_type}/{entity_id}/approvals` | Approvals attached to one thing |

No `PUT`/`DELETE` — an approval only changes via a transition, and deleting one would destroy
the audit trail it exists to keep. A rejected approval can be resubmitted (`rejected →
submitted`).

## Example uses

- **NCR workflow**: an NCR raises an `Approval` on `entity_type="ncr"` for its
  corrective-action sign-off.
- **Procurement QA**: sample/prototype/mock-up approval on `entity_type="procurement_request"`.
- **Design QA**: a drawing revision's peer-review/design-change approval on
  `entity_type="document"`, pointing at the `Document` row being reviewed.
