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
    """The record passes `store.validate_record`.

    A preview record may lack the server fields, so only absent ones get a
    placeholder. A present but invalid value is still reported.
    """
    candidate = dict(record)
    for name, placeholder in (("id", 0), ("saved_at", ""), ("page_file", "")):
        candidate.setdefault(name, placeholder)
    try:
        store.validate_record(candidate)
    except store.InvalidRecord as error:
        return GradeResult(False, str(error))
    return GradeResult(True, "record follows the schema")


def grade_tags(record: dict[str, Any]) -> GradeResult:
    """Tags are lowercase and at most MAX_TAGS. A readable record needs MIN_TAGS too."""
    tags = record.get("tags")
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        return GradeResult(False, "tags must be a list of strings")
    min_tags = 0 if _is_unreadable(record) else store.MIN_TAGS
    if not min_tags <= len(tags) <= store.MAX_TAGS:
        return GradeResult(
            False,
            f"{len(tags)} tags, need {min_tags} to {store.MAX_TAGS}",
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
    if not isinstance(summary, str):
        return GradeResult(False, "summary must be a string or null")
    words = len(summary.split())
    if words > store.MAX_SUMMARY_WORDS:
        return GradeResult(
            False, f"summary has {words} words, limit {store.MAX_SUMMARY_WORDS}"
        )
    return GradeResult(True, f"summary has {words} words")


def grade_honest_failure(
    record: dict[str, Any], expected: dict[str, Any]
) -> GradeResult:
    """An unreadable page is saved as unreadable with a null summary.

    A readable page saved as unreadable also fails: the app gave up on a page it
    could read.
    """
    if expected.get("expect") != UNREADABLE:
        if _is_unreadable(record):
            return GradeResult(False, "readable page was saved as unreadable")
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
    """Score is the share of expected tags found in the record tags (0 to 1).

    Case is ignored. With no expected tags there is nothing to score, so the
    result passes with a null score instead of a vacuous 1.0.
    """
    raw_wanted = expected.get("expected_tags") or []
    raw_found = record.get("tags") or []
    for tags in (raw_wanted, raw_found):
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            return GradeResult(False, "tags must be a list of strings", 0.0)
    wanted = {t.lower() for t in raw_wanted}
    if not wanted:
        return GradeResult(True, "no expected tags to score")
    found = wanted & {t.lower() for t in raw_found}
    score = len(found) / len(wanted)
    return GradeResult(
        score == FULL_OVERLAP, f"{len(found)} of {len(wanted)} expected tags", score
    )


GRADER_NAMES = (
    "schema",
    "tags",
    "summary_length",
    "honest_failure",
    "type_match",
    "tag_overlap",
)


def grade_record(
    record: dict[str, Any], expected: dict[str, Any]
) -> dict[str, GradeResult]:
    """All six results, keyed by grader name. Scores are not averaged.

    A record that is not a dict (for example None) fails every grader.
    """
    if not isinstance(record, dict):
        failed = GradeResult(False, "record must be a dict")
        return {name: failed for name in GRADER_NAMES}
    return {
        "schema": grade_schema(record),
        "tags": grade_tags(record),
        "summary_length": grade_summary_length(record),
        "honest_failure": grade_honest_failure(record, expected),
        "type_match": grade_type_match(record, expected),
        "tag_overlap": grade_tag_overlap(record, expected),
    }
