"""Load and check the draft expected answers in evals/expected.json.

One entry per golden page. The file is a Claude-written draft until the owner
reads each page and removes the `draft` mark.
"""

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


def _check(raw: dict) -> Expected:
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
        draft=raw["draft"],
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
        raise ValueError(
            f"{page_id}: needs {store.MIN_TAGS} to {store.MAX_TAGS} tags"
        )
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
