from app.domain.asset_qa import AssetDocumentCategory
from app.domain.contract_qa import ContractDocumentCategory
from app.domain.knowledge_management import KnowledgeManagementCategory
from app.domain.workforce_qa import WorkforceDocumentCategory

ALL_ENUMS = [
    AssetDocumentCategory,
    ContractDocumentCategory,
    KnowledgeManagementCategory,
    WorkforceDocumentCategory,
]


def test_all_category_values_are_lowercase_snake_case():
    for enum_cls in ALL_ENUMS:
        for member in enum_cls:
            assert member.value == member.value.lower().replace(" ", "_"), member


def test_new_categories_introduced_this_phase_do_not_collide():
    """WorkforceDocumentCategory.CERTIFICATE intentionally reuses the existing
    "certificate" convention from Material QA (see docs/primitives/document.md)
    — every other value introduced across these four modules should be
    distinct, so two different feature areas never silently share a category
    that isn't meant to be shared."""
    new_values = [
        member.value
        for enum_cls in ALL_ENUMS
        for member in enum_cls
        if member is not WorkforceDocumentCategory.CERTIFICATE
    ]
    assert len(new_values) == len(set(new_values))
