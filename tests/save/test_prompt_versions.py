"""The phase 3 prompt versions are logged, documented and compared (ticket #115)."""

import csv
from pathlib import Path

from mnemo.core import config

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "evals" / "results" / "runs.csv"
DOC = ROOT / "docs" / "testing" / "eval-process.md"
NOISE = 0.08


def run_rows() -> list[dict[str, str]]:
    with RUNS.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def latest_by_version() -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in run_rows():
        latest[row["prompt_version"]] = row
    return latest


def test_at_least_three_versions_besides_v1_are_logged():
    versions = {row["prompt_version"] for row in run_rows()}
    compared = versions - {"save_v1"}

    assert len(compared) >= 3
    for version in compared:
        assert (ROOT / "mnemo" / "save" / "prompts" / f"{version}.txt").exists()


def test_each_version_change_is_documented():
    doc = DOC.read_text(encoding="utf-8").lower()

    for version in ("save_v2", "save_v3", "save_v4", "save_v5"):
        assert version in doc
    for change in ("action verb", "numbered steps", "xml tags", "examples"):
        assert change in doc


def test_default_is_the_best_version_without_a_honesty_drop():
    latest = latest_by_version()
    baseline = float(latest["save_v1"]["honesty"])
    eligible = [
        row
        for row in latest.values()
        if row["save_quality"] and float(row["honesty"]) >= baseline - NOISE
    ]
    best = max(float(row["save_quality"]) for row in eligible)

    chosen = latest[config.SAVE_PROMPT_VERSION]
    assert float(chosen["save_quality"]) == best
    assert (
        ROOT / "mnemo" / "save" / "prompts" / f"{config.SAVE_PROMPT_VERSION}.txt"
    ).exists()
