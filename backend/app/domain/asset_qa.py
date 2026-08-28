"""Category conventions for Asset QA — no database, no I/O.

Asset registration, warranty tracking, lifecycle documentation, and
maintenance planning are all "a document about a physical asset, versioned
over time" — exactly what Document (category/family_id/version/status)
already covers. No new table or primitive change is needed.

QR/barcode validation is the one Asset QA item that doesn't fit here: it's a
point-in-time scan check against a physical tag, not a document — closer to
a Compliance check (a CUSTOM rule like "QR code matches asset register")
than a Document Register entry. Left out of this module; whoever builds
Asset QA's fuller scope can configure Compliance for it the same way
Contract QA's clause compliance does (see app/domain/contract_qa.py).

Assets have no primitive table of their own (out of scope for this squad's
portion of the taxonomy — configuring existing primitives only), so an
asset's documents are attached via entity_type="room": the Room an asset
lives in stands in for the asset's location, same pattern NCR and Audit use
(see docs/adr/0001-entity-reference-no-fk.md).
"""

import enum


class AssetDocumentCategory(enum.StrEnum):
    REGISTRATION = "asset_registration"
    WARRANTY = "asset_warranty"
    LIFECYCLE_RECORD = "asset_lifecycle_record"
    MAINTENANCE_PLAN = "asset_maintenance_plan"
