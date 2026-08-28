"""Proves Knowledge Management's use case works through the existing
Document endpoints alone — no new API surface, matching
app/domain/knowledge_management.py's confirmation that no new capability
was needed.
"""

from httpx import AsyncClient

from app.domain.knowledge_management import KnowledgeManagementCategory


async def test_project_global_knowledge_content_needs_no_entity(client: AsyncClient):
    response = await client.post(
        "/documents",
        json={
            "title": "Formwork Stripping Time — Lessons Learned",
            "category": KnowledgeManagementCategory.LESSON_LEARNED.value,
            "file_ref": "s3://bucket/lessons-formwork-stripping.pdf",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["entity_type"] is None
    assert body["entity_id"] is None


async def test_knowledge_content_is_filterable_by_category(client: AsyncClient):
    for category, title in (
        (KnowledgeManagementCategory.LESSON_LEARNED, "Lesson A"),
        (KnowledgeManagementCategory.BEST_PRACTICE, "Best Practice A"),
        (KnowledgeManagementCategory.STANDARD_LIBRARY, "Rebar Detailing Standard"),
    ):
        await client.post(
            "/documents",
            json={
                "title": title,
                "category": category.value,
                "file_ref": f"s3://bucket/{category.value}.pdf",
            },
        )

    best_practices = await client.get(
        f"/documents?category={KnowledgeManagementCategory.BEST_PRACTICE.value}"
    )
    assert len(best_practices.json()) == 1
    assert best_practices.json()[0]["title"] == "Best Practice A"


async def test_standard_library_update_is_a_new_version(client: AsyncClient):
    v1 = await client.post(
        "/documents",
        json={
            "title": "Rebar Detailing Standard",
            "category": KnowledgeManagementCategory.STANDARD_LIBRARY.value,
            "file_ref": "s3://bucket/rebar-standard-v1.pdf",
        },
    )
    v2 = await client.post(
        f"/documents/{v1.json()['id']}/versions",
        json={"file_ref": "s3://bucket/rebar-standard-v2.pdf"},
    )
    assert v2.json()["version"] == 2
