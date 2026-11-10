"""The committed baseline: two runs of the unchanged prompt and the noise note."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "evals" / "results" / "runs.csv"


def _baseline_rows():
    with RUNS.open(encoding="utf-8", newline="") as handle:
        return [r for r in csv.DictReader(handle) if r["prompt_version"] == "save_v1"]


def test_two_baseline_runs_have_different_run_ids():
    rows = _baseline_rows()
    assert len(rows) >= 2
    assert len({r["run_id"] for r in rows}) == len(rows)


def test_baseline_rows_have_numeric_scores_and_tokens():
    for row in _baseline_rows():
        for column in ("save_quality", "honesty", "tokens_used"):
            float(row[column])


def test_noise_level_and_session_log_are_written():
    doc = (ROOT / "docs" / "testing" / "eval-process.md").read_text(encoding="utf-8")
    assert any(line.startswith("Noise level:") for line in doc.splitlines())
    assert (ROOT / "docs" / "process" / "session-log.md").is_file()
