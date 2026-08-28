"""Category conventions for Knowledge Management — no database, no I/O.

Lessons learned, best practices, historical project records, and standard
libraries are all just documents — Document's `category` is the only thing
this feature area needed. Knowledge content is typically project-global
(entity_type=None, same as a company-wide spec per docs/primitives/document.md),
though nothing stops a caller from attaching a lesson-learned to the entity
it came from instead.

"AI recommendations" (T2 §16) is out of scope here: surfacing a
recommendation is a platform-analytics concern (Squad D's Quality Analytics/
AI-Specific QA work), not a document category — this module only covers the
record-keeping half Squad E owns.
"""

import enum


class KnowledgeManagementCategory(enum.StrEnum):
    LESSON_LEARNED = "lesson_learned"
    BEST_PRACTICE = "best_practice"
    HISTORICAL_PROJECT_RECORD = "historical_project_record"
    STANDARD_LIBRARY = "standard_library"
