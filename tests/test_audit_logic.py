import pytest

from app.domain.audit import AuditType, format_submission_comment, parse_submission_comment


def test_format_with_notes():
    comment = format_submission_comment(AuditType.INTERNAL, "Rebar cover spot-checked")
    assert comment == "[audit_type=internal] Rebar cover spot-checked"


def test_format_without_notes():
    comment = format_submission_comment(AuditType.REGULATORY, None)
    assert comment == "[audit_type=regulatory]"


@pytest.mark.parametrize("audit_type", list(AuditType))
def test_round_trip_with_notes(audit_type):
    comment = format_submission_comment(audit_type, "some findings")
    parsed = parse_submission_comment(comment)
    assert parsed.audit_type is audit_type
    assert parsed.notes == "some findings"


def test_round_trip_without_notes():
    comment = format_submission_comment(AuditType.CLIENT, None)
    parsed = parse_submission_comment(comment)
    assert parsed.audit_type is AuditType.CLIENT
    assert parsed.notes is None


def test_parse_none_comment():
    parsed = parse_submission_comment(None)
    assert parsed.audit_type is None
    assert parsed.notes is None


def test_parse_empty_comment():
    parsed = parse_submission_comment("")
    assert parsed.audit_type is None
    assert parsed.notes is None


def test_parse_comment_without_prefix_preserves_it_as_notes():
    """A comment predating this convention, or hand-written, isn't discarded
    — just reported as having no recognizable audit_type."""
    parsed = parse_submission_comment("just a plain comment, no prefix")
    assert parsed.audit_type is None
    assert parsed.notes == "just a plain comment, no prefix"


def test_parse_comment_with_unknown_type_preserves_it_as_notes():
    parsed = parse_submission_comment("[audit_type=bogus] some notes")
    assert parsed.audit_type is None
    assert parsed.notes == "[audit_type=bogus] some notes"


def test_parse_multiline_notes():
    comment = format_submission_comment(AuditType.EXTERNAL, "line one\nline two")
    parsed = parse_submission_comment(comment)
    assert parsed.audit_type is AuditType.EXTERNAL
    assert parsed.notes == "line one\nline two"
