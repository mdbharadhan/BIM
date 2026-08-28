# BIM Project — Backend + Frontend

An FastAPI + Next.js platform for construction QA, built on the OUANTUM 
Engineering Intelligence Platform's Squad E scope (BIM, Digital Twin, Design, 
Documentation & Enterprise QMS).

## backend/ (FastAPI, async SQLAlchemy 2.0, Pydantic v2)

cd backend
pip install -r requirements.txt # or: fastapi uvicorn sqlalchemy aiosqlite pydantic-settings
uvicorn app.main:app --reload --port 8000
Or with `uv`:
uv sync
PYTHONPATH=backend uv run uvicorn app.main:app --reload --port 8000

Run tests:
PYTHONPATH=backend uv run pytest
## frontend/ (Next.js 16, TypeScript, Tailwind v4)
cd frontend
npm install
npm run dev


Open http://localhost:3000

API base URL is set in `frontend/.env.local` -> `NEXT_PUBLIC_API_URL`

## What's in this repo

### BIM core (Building/Floor/Room/Structural Element)
Full CRUD, frontend consumes `buildings`, `floors` (+ `/buildings/{id}/floors`), 
`rooms` (+ `/floors/{id}/rooms`), `structural-elements` (+ `/rooms/{id}/elements`).

### Shared QA primitives
Four reusable building blocks most of Squad E's scope configures rather than 
rebuilding — see `docs/primitives/` and `CONTEXT.md` for the full domain glossary:
- **Checklist** — templates + filled instances (ITPs, punch lists, inspections)
- **Approval** — a draft→submitted→under_review→approved/rejected/closed state 
  machine with a full audit trail (`ApprovalEvent`)
- **Document register** — versioned documents grouped by family, with supersession
- **Compliance** — standards → rules → checks, with a pass/fail/skip evaluator 
  that never fabricates a result for something that wasn't actually measured

All four attach to any real-world entity via a generic `entity_type`/`entity_id` 
pair with no foreign key (see `docs/adr/0001-entity-reference-no-fk.md`) — so 
they can point at tables owned by other squads that don't exist yet.

### Feature layers built on the primitives
- **NCR workflow** (`/ncrs`) — non-conformance reports over Approval
- **Audit workflow** (`/audits`) — internal/external/client/regulatory audits over Approval
- **Design QA review/approval** (`/design-reviews`) — design/peer/spec reviews over Approval
- **Compliance evaluation** (`/compliance-evaluations`) — batch-evaluates 
  measurements against a standard's seeded rules, records checks, and reports 
  what was skipped and why
- **Checklist completion tracking** — distinguishes "completed" from "fully passed"
- **Enterprise QMS** (`/enterprise-qms/{register}/...`) — current version + 
  history lookups over the Document register (risk register, compliance 
  register, supplier management)
- **Seeded reference data** — IS 383 (fine aggregate), LEED v4 BD+C, IGBC, 
  GRIHA, BREEAM standards; Concrete Pour, Material Delivery, Pre-Commissioning, 
  and Final Handover checklist templates

### Not yet built
- **BIM-Vision** (perception/geometry ML subsystem) — separate track, in progress
- Certification-level rollup for sustainability standards (needs an aggregation 
  feature on top of the compliance evaluator — flagged as a gap, not built)
- Frontend coverage for anything beyond the core BIM CRUD pages

## Notes
- No upload/search endpoints exist on the backend for BIM core entities, so 
  those frontend pages were intentionally omitted.
- Dedicated metadata for Audit/Design Review (e.g. audit_type) is currently 
  encoded into Approval's comment field rather than a real column — a 
  documented workaround, not the intended long-term design (see 
  `app/domain/audit.py`).
