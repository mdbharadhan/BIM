from pydantic import BaseModel


class ChecklistCompletionStatus(BaseModel):
    instance_id: int
    total_items: int
    completed_items: int
    pending_required_items: list[str]
    failed_required_items: list[str]
    is_complete: bool
    is_fully_passed: bool
