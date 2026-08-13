# Compliance

A standard (e.g. "IS 383", "LEED") owns a set of named rules — either a numeric threshold
(`operator`/`threshold_value`/`unit`) or a non-numeric requirement recorded as `rule_text`
(e.g. "Material Test Certificate must be provided"). A check records one rule evaluated
against one real thing, with the actual measured value and result. The primitive never
evaluates a rule automatically — `result` is always set by whoever performs the check.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/compliance-standards` | Create a standard |
| GET | `/compliance-standards` | List standards |
| GET/PUT/DELETE | `/compliance-standards/{id}` | Read / update / delete |
| POST | `/compliance-standards/{id}/rules` | Add a rule to a standard |
| GET | `/compliance-standards/{id}/rules` | List a standard's rules |
| GET/PUT/DELETE | `/compliance-rules/{id}` | Read / update / delete a rule |
| POST | `/compliance-checks` | Record a check against `entity_type`/`entity_id` |
| GET | `/compliance-checks` / `/{id}` | List / read checks |
| GET | `/compliance-rules/{id}/checks` | Checks recorded against one rule |
| GET | `/entities/{entity_type}/{entity_id}/compliance-checks` | Checks against one thing |

## Example uses

- **Sand quality QA**: standard `"IS 383"`, rule `"Silt content max"`
  (`parameter_name="silt_content_percent"`, `operator="lt"`, `threshold_value=5`, `unit="%"`),
  checked against `entity_type="material_delivery"` for each sand delivery.
- **Sustainability Compliance**: standards `"LEED"`, `"IGBC"`, `"GRIHA"`, `"BREEAM"`, each with
  their own rule sets, checked against `entity_type="building"`.
- **Fire & Life Safety QA**: a rule with `rule_text="Fire alarm functional test passed"` and no
  numeric threshold, checked against `entity_type="structural_element"`.
