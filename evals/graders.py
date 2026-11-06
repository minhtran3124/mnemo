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


@dataclass(frozen=True)
class GradeResult:
    passed: bool
    reason: str
    score: float | None = None


def grade_schema(record: dict[str, Any]) -> GradeResult:
    """The record passes `store.validate_record` once the server fields are filled."""
    candidate = {**record, "id": 0, "saved_at": "", "page_file": ""}
    try:
        store.validate_record(candidate)
    except store.InvalidRecord as error:
        return GradeResult(False, str(error))
    return GradeResult(True, "record follows the schema")


def grade_tags(record: dict[str, Any]) -> GradeResult:
    """MIN_TAGS to MAX_TAGS tags, all lowercase. An unreadable record is not checked."""
    if record["page_status"] == UNREADABLE:
        return GradeResult(True, "unreadable record, tags not checked")
    tags = record["tags"]
    if not store.MIN_TAGS <= len(tags) <= store.MAX_TAGS:
        return GradeResult(
            False, f"{len(tags)} tags, need {store.MIN_TAGS} to {store.MAX_TAGS}"
        )
    upper = [t for t in tags if t != t.lower()]
    if upper:
        return GradeResult(False, f"tags not lowercase: {', '.join(upper)}")
    return GradeResult(True, f"{len(tags)} lowercase tags")


def grade_summary_length(record: dict[str, Any]) -> GradeResult:
    """The summary has at most MAX_SUMMARY_WORDS words."""
    words = len((record["summary"] or "").split())
    if words > store.MAX_SUMMARY_WORDS:
        return GradeResult(
            False, f"summary has {words} words, limit {store.MAX_SUMMARY_WORDS}"
        )
    return GradeResult(True, f"summary has {words} words")


def grade_honest_failure(
    record: dict[str, Any], expected: dict[str, Any]
) -> GradeResult:
    """When `expect` is unreadable: page_status is unreadable and summary is null."""
    if expected["expect"] != UNREADABLE:
        return GradeResult(True, "page is expected to be readable")
    if record["page_status"] != UNREADABLE:
        return GradeResult(False, "unreadable page was not marked unreadable")
    if record["summary"] is not None:
        return GradeResult(False, "unreadable page has a summary")
    return GradeResult(True, "unreadable page saved with a null summary")


def grade_type_match(record: dict[str, Any], expected: dict[str, Any]) -> GradeResult:
    """The record type equals the expected type."""
    got, want = record["type"], expected["expected_type"]
    if got == want:
        return GradeResult(True, f"type is {got}")
    return GradeResult(False, f"type is {got}, expected {want}")


def grade_tag_overlap(record: dict[str, Any], expected: dict[str, Any]) -> GradeResult:
    """Score is the share of expected tags found in the record tags (0 to 1)."""
    wanted = expected["expected_tags"]
    if not wanted:
        return GradeResult(True, "no expected tags", 1.0)
    found = [t for t in wanted if t in record["tags"]]
    score = len(found) / len(wanted)
    return GradeResult(
        score == 1.0, f"{len(found)} of {len(wanted)} expected tags", score
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
