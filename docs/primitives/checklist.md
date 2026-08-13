# Checklist

A reusable **template** (ordered items, each optionally required and/or requiring photo
evidence) that gets instantiated into a filled-out **instance** attached to any real-world
thing. An instance's items are a snapshot taken at creation time — editing the template
later never rewrites an already-in-progress or completed instance.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/checklist-templates` | Create a template, optionally with nested items |
| GET | `/checklist-templates` | List templates |
| GET/PUT/DELETE | `/checklist-templates/{id}` | Read / update / delete a template |
| POST | `/checklist-templates/{id}/items` | Add an item to a template |
| DELETE | `/checklist-templates/{id}/items/{item_id}` | Remove a template item |
| POST | `/checklist-instances` | Instantiate a template against `entity_type`/`entity_id` |
| GET | `/checklist-instances` | List instances |
| GET/DELETE | `/checklist-instances/{id}` | Read / delete an instance |
| PATCH | `/checklist-instances/{id}/items/{item_id}` | Mark an item pass/fail/na, attach evidence |
| GET | `/entities/{entity_type}/{entity_id}/checklist-instances` | Instances attached to one thing |

Instance `status` (`not_started`/`in_progress`/`completed`) is derived automatically as items
are marked, based on whether every item has left the `pending` state.

## Example uses

- **Inspection Requests / ITPs**: a "Concrete Pour Checklist" template instantiated once per
  pour, attached to `entity_type="structural_element"`.
- **Punch lists / snag lists**: a per-room punch-list template instantiated at
  `entity_type="room"` for each unit at handover.
- **Commissioning QA**: a pre-commissioning checklist instantiated per system, with
  `requires_evidence=true` items for anything needing a photo before sign-off.
