"""Tests for the draft expected answers in evals/expected.json."""

import json
from pathlib import Path

import pytest

from evals import golden

ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = ROOT / "evals"
PAGES = json.loads((EVALS_DIR / "pages.json").read_text(encoding="utf-8"))
HELD_OUT = {"S-03", "S-08", "S-09", "S-12", "S-13"}
HARD = {"S-08", "S-09", "S-12", "S-13"}


def _entry(page_id, held_out=False, hard_case=False):
    return {
        "id": page_id,
        "expected_type": "article",
        "expected_tags": ["one", "two", "three"],
        "key_facts": ["fact a", "fact b"],
        "held_out": held_out,
        "hard_case": hard_case,
        "expect": "ok",
        "note": "",
        "draft": True,
    }


def _valid():
    entries = []
    for number in range(1, 16):
        page_id = f"S-{number:02d}"
        entries.append(
            _entry(page_id, page_id in HELD_OUT, page_id in HARD)
        )
    return entries


def _write(tmp_path, entries):
    path = tmp_path / "expected.json"
    path.write_text(json.dumps(entries), encoding="utf-8")
    return path


def test_load_expected_accepts_a_valid_file(tmp_path):
    loaded = golden.load_expected(_write(tmp_path, _valid()))
    assert [e.id for e in loaded] == [f"S-{n:02d}" for n in range(1, 16)]
    assert loaded[0].draft is True


def test_rejects_wrong_tag_count(tmp_path):
    for count in (2, 7):
        entries = _valid()
        entries[0]["expected_tags"] = [f"tag{i}" for i in range(count)]
        with pytest.raises(ValueError):
            golden.load_expected(_write(tmp_path, entries))


def test_rejects_type_outside_store_types(tmp_path):
    entries = _valid()
    entries[0]["expected_type"] = "podcast"
    with pytest.raises(ValueError):
        golden.load_expected(_write(tmp_path, entries))


def test_rejects_wrong_key_fact_count(tmp_path):
    for count in (1, 5):
        entries = _valid()
        entries[0]["key_facts"] = [f"fact {i}" for i in range(count)]
        with pytest.raises(ValueError):
            golden.load_expected(_write(tmp_path, entries))


def test_rejects_bad_held_out_set(tmp_path):
    too_few = _valid()
    too_few[2]["held_out"] = False
    with pytest.raises(ValueError):
        golden.load_expected(_write(tmp_path, too_few))

    few_hard = _valid()
    for entry in few_hard:
        entry["hard_case"] = entry["id"] == "S-03" or entry["id"] == "S-08"
    few_hard[2]["hard_case"] = True
    few_hard[7]["hard_case"] = False
    with pytest.raises(ValueError):
        golden.load_expected(_write(tmp_path, few_hard))


def test_committed_file_matches_pages_and_is_draft():
    loaded = golden.load_expected()
    assert [e.id for e in loaded] == [p["id"] for p in PAGES]
    for entry, page in zip(loaded, PAGES, strict=True):
        assert entry.expect == page["expect"]
        assert entry.draft is True
    assert {e.id for e in loaded if e.expect == "unreadable"} == {
        "S-08",
        "S-10",
        "S-15",
    }
    assert {e.id for e in loaded if e.held_out} == HELD_OUT


def test_prompts_do_not_leak_held_out_pages():
    held = [e for e in golden.load_expected() if e.held_out]
    urls = [p["url"] for p in PAGES if p["id"] in {e.id for e in held}]
    needles = urls + [fact for e in held for fact in e.key_facts]
    for prompt in (ROOT / "prompts").glob("*.txt"):
        text = prompt.read_text(encoding="utf-8").lower()
        for needle in needles:
            assert needle.lower() not in text, f"{prompt.name} leaks {needle}"
