import enum


class ElementType(enum.StrEnum):
    WALL = "wall"
    BEAM = "beam"
    COLUMN = "column"
    SLAB = "slab"
    DOOR = "door"
    WINDOW = "window"
    STAIR = "stair"


class ChecklistInstanceStatus(enum.StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ChecklistItemState(enum.StrEnum):
    PENDING = "pending"
    PASS_ = "pass"  # nosec B105
    FAIL = "fail"
    NA = "na"


class ApprovalStatus(enum.StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"


class DocumentStatus(enum.StrEnum):
    DRAFT = "draft"
    CURRENT = "current"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ComplianceOperator(enum.StrEnum):
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    EQ = "eq"
    BETWEEN = "between"
    EXISTS = "exists"
    CUSTOM = "custom"


class ComplianceResult(enum.StrEnum):
    PASS_ = "pass"  # nosec B105
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"
