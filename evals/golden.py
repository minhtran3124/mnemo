"""Load and check the draft expected answers in evals/expected.json.

One entry per golden page. The file is a Claude-written draft until the owner
reads each page and removes the `draft` mark.
"""

# ruff: noqa: TRY004
import json
from dataclasses import dataclass
from pathlib import Path

import store

DEFAULT_PATH = Path(__file__).resolve().parent / "expected.json"
EXPECTS = {"ok", "unreadable"}
MIN_FACTS = 2
MAX_FACTS = 4
HELD_OUT_COUNT = 5
MIN_HELD_OUT_HARD = 2


@dataclass(frozen=True)
class Expected:
    id: str
    expected_type: str
    expected_tags: tuple[str, ...]
    key_facts: tuple[str, ...]
    held_out: bool
    hard_case: bool
    expect: str
    note: str
    draft: bool


REQUIRED = (
    "id",
    "expected_type",
    "expected_tags",
    "key_facts",
    "held_out",
    "hard_case",
    "expect",
)


def _is_text_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _check_shape(raw: object) -> None:
    """Raise ValueError when an entry is not an object with the right keys and types."""
    if not isinstance(raw, dict):
        raise ValueError("each entry must be an object")
    page_id = raw.get("id", "?")
    missing = [key for key in REQUIRED if key not in raw]
    if missing:
        raise ValueError(f"{page_id}: missing keys {missing}")
    for key in ("id", "expected_type", "expect"):
        if not isinstance(raw[key], str):
            raise ValueError(f"{page_id}: {key} must be a string")
    for key in ("expected_tags", "key_facts"):
        if not _is_text_list(raw[key]):
            raise ValueError(f"{page_id}: {key} must be a list of strings")
    for key in ("held_out", "hard_case"):
        if not isinstance(raw[key], bool):
            raise ValueError(f"{page_id}: {key} must be true or false")
    if not isinstance(raw.get("note", ""), str):
        raise ValueError(f"{page_id}: note must be a string")


def _check(raw: dict) -> Expected:
    _check_shape(raw)
    page_id = raw["id"]
    entry = Expected(
        id=page_id,
        expected_type=raw["expected_type"],
        expected_tags=tuple(raw["expected_tags"]),
        key_facts=tuple(raw["key_facts"]),
        held_out=raw["held_out"],
        hard_case=raw["hard_case"],
        expect=raw["expect"],
        note=raw.get("note", ""),
        draft=raw.get("draft", False),
    )
    if entry.expected_type not in store.TYPES:
        raise ValueError(f"{page_id}: type must be one of {sorted(store.TYPES)}")
    if entry.expect not in EXPECTS:
        raise ValueError(f"{page_id}: expect must be one of {sorted(EXPECTS)}")
    if not isinstance(entry.draft, bool):
        raise ValueError(f"{page_id}: draft must be true or false")
    if entry.expect == "unreadable":
        if entry.expected_tags or entry.key_facts:
            raise ValueError(f"{page_id}: unreadable needs no tags and no key facts")
        return entry
    if not store.MIN_TAGS <= len(entry.expected_tags) <= store.MAX_TAGS:
        raise ValueError(f"{page_id}: needs {store.MIN_TAGS} to {store.MAX_TAGS} tags")
    if any(tag != tag.lower() for tag in entry.expected_tags):
        raise ValueError(f"{page_id}: tags must be lowercase")
    if not MIN_FACTS <= len(entry.key_facts) <= MAX_FACTS:
        raise ValueError(f"{page_id}: needs {MIN_FACTS} to {MAX_FACTS} key facts")
    return entry


def load_expected(path: Path = DEFAULT_PATH) -> list[Expected]:
    """Read the file and return its entries in file order. Raise ValueError on a broken rule."""
    entries = [_check(raw) for raw in json.loads(path.read_text(encoding="utf-8"))]
    held = [entry for entry in entries if entry.held_out]
    if len(held) != HELD_OUT_COUNT:
        raise ValueError(f"exactly {HELD_OUT_COUNT} entries must be held out")
    if sum(entry.hard_case for entry in held) < MIN_HELD_OUT_HARD:
        raise ValueError(
            f"at least {MIN_HELD_OUT_HARD} held-out entries must be hard cases"
        )
    return entries
