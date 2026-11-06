"""Code graders for a saved-bookmark record (Phase 2 eval harness)."""

from typing import Any

from evals import graders


def make_record(**overrides: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": 1,
        "saved_at": "2026-01-01T00:00:00+00:00",
        "page_file": "pages/1.txt",
        "url": "https://example.com/a",
        "url_clean": "https://example.com/a",
        "type": "article",
        "title": "An article",
        "page_status": "ok",
        "summary": "A short summary of the page.",
        "tags": ["python", "testing", "tools"],
        "reason": "",
        "reason_source": "user",
        "folder": None,
        "opened_count": 0,
    }
    record.update(overrides)
    return record


def make_expected(**overrides: Any) -> dict[str, Any]:
    expected: dict[str, Any] = {
        "expect": "readable",
        "expected_type": "article",
        "expected_tags": ["python", "testing", "tools"],
    }
    expected.update(overrides)
    return expected


def test_schema_valid_passes_and_missing_field_fails():
    assert graders.grade_schema(make_record()).passed
    record = make_record()
    del record["title"]
    result = graders.grade_schema(record)
    assert not result.passed
    assert "title" in result.reason


def test_schema_checks_present_server_fields_and_allows_absent_ones():
    result = graders.grade_schema(make_record(id="x"))
    assert not result.passed
    assert "id" in result.reason
    preview = make_record()
    for name in ("id", "saved_at", "page_file"):
        del preview[name]
    assert graders.grade_schema(preview).passed


def test_tag_count_out_of_range_fails():
    assert graders.grade_tags(make_record(tags=["a", "b", "c"])).passed
    assert not graders.grade_tags(make_record(tags=["a", "b"])).passed
    assert not graders.grade_tags(make_record(tags=list("abcdefg"))).passed


def test_uppercase_tag_fails():
    result = graders.grade_tags(make_record(tags=["python", "Testing", "tools"]))
    assert not result.passed


def test_unreadable_record_still_checks_tag_limits():
    base = {"page_status": "unreadable", "summary": None}
    assert graders.grade_tags(make_record(tags=[], **base)).passed
    assert not graders.grade_tags(make_record(tags=["Python"], **base)).passed
    assert not graders.grade_tags(make_record(tags=list("abcdefg"), **base)).passed


def test_summary_of_61_words_fails():
    assert not graders.grade_summary_length(make_record(summary="w " * 61)).passed


def test_summary_of_60_words_passes():
    assert graders.grade_summary_length(make_record(summary="w " * 60)).passed


def test_non_string_summary_fails_without_raising():
    for bad in (123, ["a", "b"], {"a": 1}):
        result = graders.grade_summary_length(make_record(summary=bad))
        assert not result.passed


def test_unreadable_with_null_summary_passes_honest_failure():
    record = make_record(page_status="unreadable", summary=None, tags=[])
    result = graders.grade_honest_failure(record, make_expected(expect="unreadable"))
    assert result.passed


def test_unreadable_expected_page_with_summary_fails_honest_failure():
    record = make_record(page_status="ok", summary="Invented text.")
    result = graders.grade_honest_failure(record, make_expected(expect="unreadable"))
    assert not result.passed


def test_readable_expected_page_saved_unreadable_fails_honest_failure():
    record = make_record(page_status="unreadable", summary=None, tags=[])
    result = graders.grade_honest_failure(record, make_expected(expect="readable"))
    assert not result.passed


def test_type_match_true_and_false():
    expected = make_expected()
    assert graders.grade_type_match(make_record(), expected).passed
    assert not graders.grade_type_match(make_record(type="tool"), expected).passed


def test_tag_overlap_is_two_thirds():
    record = make_record(tags=["python", "testing", "other"])
    result = graders.grade_tag_overlap(record, make_expected())
    assert result.score is not None
    assert abs(result.score - 2 / 3) < 1e-9
    assert not result.passed


def test_tag_overlap_ignores_case():
    record = make_record(tags=["Python", "TESTING", "tools"])
    result = graders.grade_tag_overlap(record, make_expected())
    assert result.score == 1.0
    assert result.passed


def test_tag_overlap_with_no_expected_tags_has_no_score():
    for wanted in ([], None):
        result = graders.grade_tag_overlap(
            make_record(), make_expected(expected_tags=wanted)
        )
        assert result.passed
        assert result.score is None


def test_tag_overlap_fails_on_malformed_tags_without_raising():
    for bad in ("python", [["python"]], [{"a": 1}], 5):
        result = graders.grade_tag_overlap(make_record(tags=bad), make_expected())
        assert not result.passed
        assert result.score == 0.0
    result = graders.grade_tag_overlap(make_record(), make_expected(expected_tags="ab"))
    assert not result.passed


def test_grade_record_returns_all_six_results():
    results = graders.grade_record(make_record(), make_expected())
    assert set(results) == {
        "schema",
        "tags",
        "summary_length",
        "honest_failure",
        "type_match",
        "tag_overlap",
    }


def test_grade_record_fails_every_grader_for_a_non_dict_record():
    for bad in (None, "text", ["a"]):
        results = graders.grade_record(bad, make_expected())
        assert len(results) == 6
        assert not any(result.passed for result in results.values())
