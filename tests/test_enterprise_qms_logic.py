from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.domain.enterprise_qms import RegisterCategory, pick_most_recent


@dataclass
class _Stamped:
    label: str
    created_at: datetime


def test_pick_most_recent_of_empty_list_is_none():
    assert pick_most_recent([]) is None


def test_pick_most_recent_single_item():
    only = _Stamped("only", datetime.now(UTC))
    assert pick_most_recent([only]) is only


def test_pick_most_recent_picks_the_latest_timestamp():
    now = datetime.now(UTC)
    oldest = _Stamped("oldest", now - timedelta(days=2))
    middle = _Stamped("middle", now - timedelta(days=1))
    newest = _Stamped("newest", now)

    assert pick_most_recent([oldest, newest, middle]) is newest


def test_register_category_values_are_stable_strings():
    """These strings are the actual Document.category values callers will
    search on — changing them silently would orphan existing data."""
    assert RegisterCategory.RISK_REGISTER.value == "risk_register"
    assert RegisterCategory.COMPLIANCE_REGISTER.value == "compliance_register"
    assert RegisterCategory.SUPPLIER_MANAGEMENT.value == "supplier_management"
