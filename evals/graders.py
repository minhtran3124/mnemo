"""Plain code graders for one saved-bookmark record. No network, no model.

Each grader checks the record from `save.preview` against the save rules or one
expected entry. Every limit is read from `store`, never copied here.

An expected entry is a dict with the keys `expect` ("readable" or
"unreadable"), `expected_type` and `expected_tags`.
"""

from dataclasses import dataclass
from typing import Any

import store

UNREADABLE = "unreadable"
FULL_OVERLAP = 1.0


@dataclass(frozen=True)
class GradeResult:
    passed: bool
    reason: str
    score: float | None = None


def _is_unreadable(record: dict[str, Any]) -> bool:
    return record.get("page_status") == UNREADABLE


def grade_schema(record: dict[str, Any]) -> GradeResult:
    """The record passes `store.validate_record` once server fields are filled."""
    candidate = dict(record)
    candidate.update(id=0, saved_at="", page_file="")
    try:
        store.validate_record(candidate)
    except store.InvalidRecord as error:
        return GradeResult(False, str(error))
    return GradeResult(True, "record follows the schema")


def grade_tags(record: dict[str, Any]) -> GradeResult:
    """A readable record has MIN_TAGS to MAX_TAGS tags, all lowercase."""
    if _is_unreadable(record):
        return GradeResult(True, "unreadable record, tags not checked")
    tags = record.get("tags")
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        return GradeResult(False, "tags must be a list of strings")
    if not store.MIN_TAGS <= len(tags) <= store.MAX_TAGS:
        return GradeResult(
            False,
            f"{len(tags)} tags, need {store.MIN_TAGS} to {store.MAX_TAGS}",
        )
    upper = [t for t in tags if t != t.lower()]
    if upper:
        return GradeResult(False, f"tags not lowercase: {', '.join(upper)}")
    return GradeResult(True, f"{len(tags)} lowercase tags")


def grade_summary_length(record: dict[str, Any]) -> GradeResult:
    """The summary has at most MAX_SUMMARY_WORDS words. A null summary passes."""
    summary = record.get("summary")
    if summary is None:
        return GradeResult(True, "no summary to count")
    words = len(summary.split())
    if words > store.MAX_SUMMARY_WORDS:
        return GradeResult(
            False, f"summary has {words} words, limit {store.MAX_SUMMARY_WORDS}"
        )
    return GradeResult(True, f"summary has {words} words")


def grade_honest_failure(
    record: dict[str, Any], expected: dict[str, Any]
) -> GradeResult:
    """An unreadable page is saved as unreadable with a null summary."""
    if expected.get("expect") != UNREADABLE:
        return GradeResult(True, "page is expected to be readable")
    if record.get("page_status") != UNREADABLE:
        return GradeResult(False, "unreadable page was not marked unreadable")
    if record.get("summary") is not None:
        return GradeResult(False, "unreadable page has a summary")
    return GradeResult(True, "unreadable page saved with a null summary")


def grade_type_match(record: dict[str, Any], expected: dict[str, Any]) -> GradeResult:
    """The record type equals the expected type."""
    got, want = record.get("type"), expected.get("expected_type")
    if got == want:
        return GradeResult(True, f"type is {got}")
    return GradeResult(False, f"type is {got}, expected {want}")


def grade_tag_overlap(record: dict[str, Any], expected: dict[str, Any]) -> GradeResult:
    """Score is the share of expected tags found in the record tags (0 to 1)."""
    wanted = set(expected.get("expected_tags") or [])
    if not wanted:
        return GradeResult(True, "no expected tags", FULL_OVERLAP)
    found = wanted & set(record.get("tags") or [])
    score = len(found) / len(wanted)
    return GradeResult(
        score == FULL_OVERLAP, f"{len(found)} of {len(wanted)} expected tags", score
    )


def grade_record(
    record: dict[str, Any], expected: dict[str, Any]
) -> dict[str, GradeResult]:
    """All six results, keyed by grader name. Scores are not averaged."""
    return {
        "schema": grade_schema(record),
        "tags": grade_tags(record),
        "summary_length": grade_summary_length(record),
        "honest_failure": grade_honest_failure(record, expected),
        "type_match": grade_type_match(record, expected),
        "tag_overlap": grade_tag_overlap(record, expected),
    }
