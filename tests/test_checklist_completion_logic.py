import pytest

from app.domain.checklist_completion import ItemSnapshot, summarize
from app.domain.enums import ChecklistItemState

PENDING = ChecklistItemState.PENDING
PASS_ = ChecklistItemState.PASS_
FAIL = ChecklistItemState.FAIL
NA = ChecklistItemState.NA


def _item(label: str, state, is_required: bool = True) -> ItemSnapshot:
    return ItemSnapshot(label=label, state=state, is_required=is_required)


def test_empty_instance_is_not_complete():
    summary = summarize([])
    assert summary.is_complete is False
    assert summary.is_fully_passed is False
    assert summary.total_items == 0


def test_all_pending_is_not_complete():
    summary = summarize([_item("a", PENDING), _item("b", PENDING)])
    assert summary.is_complete is False
    assert summary.completed_items == 0
    assert summary.pending_required_items == ["a", "b"]


def test_partial_progress_is_not_complete():
    summary = summarize([_item("a", PASS_), _item("b", PENDING)])
    assert summary.is_complete is False
    assert summary.pending_required_items == ["b"]


def test_all_items_addressed_is_complete():
    summary = summarize([_item("a", PASS_), _item("b", NA)])
    assert summary.is_complete is True
    assert summary.completed_items == 2


def test_all_pass_is_fully_passed():
    summary = summarize([_item("a", PASS_), _item("b", PASS_)])
    assert summary.is_complete is True
    assert summary.is_fully_passed is True
    assert summary.failed_required_items == []


def test_failed_required_item_is_complete_but_not_fully_passed():
    """The headline distinction: status='completed' on the primitive doesn't
    mean every required item passed."""
    summary = summarize([_item("a", PASS_), _item("b", FAIL)])
    assert summary.is_complete is True
    assert summary.is_fully_passed is False
    assert summary.failed_required_items == ["b"]


def test_failed_optional_item_does_not_block_fully_passed():
    summary = summarize([_item("a", PASS_), _item("b", FAIL, is_required=False)])
    assert summary.is_fully_passed is True
    assert summary.failed_required_items == []


@pytest.mark.parametrize("state", [PENDING, PASS_, FAIL, NA])
def test_single_item_states(state):
    summary = summarize([_item("a", state)])
    assert summary.total_items == 1
