import pytest

from app.domain.design_review import (
    DesignReviewType,
    format_submission_comment,
    parse_submission_comment,
)


def test_format_with_notes():
    comment = format_submission_comment(DesignReviewType.PEER_REVIEW, "Reviewed by structural lead")
    assert comment == "[review_type=peer_review] Reviewed by structural lead"


def test_format_without_notes():
    comment = format_submission_comment(DesignReviewType.SPEC_REVIEW, None)
    assert comment == "[review_type=spec_review]"


@pytest.mark.parametrize("review_type", list(DesignReviewType))
def test_round_trip_with_notes(review_type):
    comment = format_submission_comment(review_type, "some findings")
    parsed = parse_submission_comment(comment)
    assert parsed.review_type is review_type
    assert parsed.notes == "some findings"


def test_round_trip_without_notes():
    comment = format_submission_comment(DesignReviewType.VALUE_ENGINEERING, None)
    parsed = parse_submission_comment(comment)
    assert parsed.review_type is DesignReviewType.VALUE_ENGINEERING
    assert parsed.notes is None


def test_parse_none_comment():
    parsed = parse_submission_comment(None)
    assert parsed.review_type is None
    assert parsed.notes is None


def test_parse_empty_comment():
    parsed = parse_submission_comment("")
    assert parsed.review_type is None
    assert parsed.notes is None


def test_parse_comment_without_prefix_preserves_it_as_notes():
    parsed = parse_submission_comment("just a plain comment, no prefix")
    assert parsed.review_type is None
    assert parsed.notes == "just a plain comment, no prefix"


def test_parse_comment_with_unknown_type_preserves_it_as_notes():
    parsed = parse_submission_comment("[review_type=bogus] some notes")
    assert parsed.review_type is None
    assert parsed.notes == "[review_type=bogus] some notes"


def test_parse_multiline_notes():
    comment = format_submission_comment(
        DesignReviewType.CONSTRUCTABILITY_REVIEW, "line one\nline two"
    )
    parsed = parse_submission_comment(comment)
    assert parsed.review_type is DesignReviewType.CONSTRUCTABILITY_REVIEW
    assert parsed.notes == "line one\nline two"
