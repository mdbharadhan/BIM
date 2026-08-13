# Document

Tracks documents with title, category, version, status, and who uploaded them. Each version
is its own row; uploading a new version supersedes the old one rather than overwriting it, so
history is never lost. Every version of "the same" document shares a `family_id`, letting you
ask "what's the current version of this?" directly instead of walking a chain.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/documents` | Upload a new document (starts a new family, `version=1`) |
| GET | `/documents?category=&status=` | Search/filter |
| GET/PUT/DELETE | `/documents/{id}` | Read / update metadata / delete |
| POST | `/documents/{id}/versions` | Upload a new version (supersedes this one) |
| GET | `/documents/{id}/versions` | All versions in this document's family, oldest first |
| GET | `/entities/{entity_type}/{entity_id}/documents` | Documents attached to one thing |

`entity_type`/`entity_id` are optional — a document can be project-global (a contract, a
company-wide spec) rather than tied to one specific thing.

## Example uses

- **Documentation Management**: IFC drawings, shop drawings, and as-built drawings tracked
  with `category="drawing"`, each revision uploaded as a new version.
- **Material QA**: a Material Test Certificate uploaded with `category="certificate"`,
  attached to `entity_type="material_delivery"`.
- **Workforce QA**: an inspector's certification document (`category="certificate"`) —
  re-certification is a new version, not a new record.
