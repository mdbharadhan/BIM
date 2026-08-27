"""Pure derivation of a checklist instance's completion — no database, no I/O.

ChecklistInstance.status (see the primitive) already tracks whether every
item has left `pending`; it cannot tell "every item was addressed" apart from
"every item passed", since a required item can be marked `fail` and still
count as no-longer-pending. That distinction is what this module adds.
"""

from dataclasses import dataclass

from app.domain.enums import ChecklistItemState


@dataclass(frozen=True)
class ItemSnapshot:
    label: str
    state: ChecklistItemState
    is_required: bool


@dataclass(frozen=True)
class CompletionSummary:
    total_items: int
    completed_items: int
    pending_required_items: list[str]
    failed_required_items: list[str]
    is_complete: bool
    is_fully_passed: bool


def summarize(items: list[ItemSnapshot]) -> CompletionSummary:
    completed = [i for i in items if i.state is not ChecklistItemState.PENDING]
    pending_required = [
        i.label for i in items if i.is_required and i.state is ChecklistItemState.PENDING
    ]
    failed_required = [
        i.label for i in items if i.is_required and i.state is ChecklistItemState.FAIL
    ]

    # An empty instance (a template with no items) is never "complete" —
    # mirrors ChecklistService._sync_instance_status, which leaves it
    # not_started rather than treating a vacuous instance as done.
    is_complete = bool(items) and len(completed) == len(items)
    is_fully_passed = is_complete and not failed_required

    return CompletionSummary(
        total_items=len(items),
        completed_items=len(completed),
        pending_required_items=pending_required,
        failed_required_items=failed_required,
        is_complete=is_complete,
        is_fully_passed=is_fully_passed,
    )
