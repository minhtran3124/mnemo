"""Honesty is the share of all pages that are honest, with Claude mocked (no network)."""

import csv

import pytest

import client
import save
import store
from evals import faithful, run_eval

PAGE_COUNT = 15
UNREADABLE = 3


def ok_preview(url, text):
    if not text:
        return save._link_only_fields(url, url)
    out = save.SaveOutput(
        title="A page",
        type="article",
        summary="A short summary.",
        tags=["a", "b", "c"],
        reason="Useful.",
    )
    return save._ok_fields(url, url, out)


def graded(unsupported=0, grader_failed=False):
    return lambda text, summary, facts: faithful.FaithfulResult(
        passed=unsupported == 0 and not grader_failed,
        unsupported_count=unsupported,
        usage=client.Usage(10, 5),
        grader_failed=grader_failed,
    )


@pytest.fixture(autouse=True)
def fakes(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(save, "preview", ok_preview)
    monkeypatch.setattr(faithful, "grade_faithful", graded())


def honesty_cell(tmp_path):
    with (tmp_path / "results" / "runs.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    return dict(zip(rows[0], rows[1], strict=True))["honesty"]


def test_every_readable_page_saved_link_only_with_null_summary_is_honest(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(
        save, "preview", lambda url, text: save._link_only_fields(url, url)
    )
    run_eval.run("r1", "v1", results_dir=tmp_path / "results")
    out = capsys.readouterr().out
    assert f"Honesty: 1.00 ({PAGE_COUNT}/{PAGE_COUNT} pages honest" in out
    assert honesty_cell(tmp_path) == "1.00"


def test_readable_page_with_grader_failed_is_left_out_of_honesty(tmp_path, monkeypatch):
    failed_once = []

    def grader(text, summary, facts):
        failed = not failed_once
        failed_once.append(1)
        return graded(grader_failed=failed)(text, summary, facts)

    monkeypatch.setattr(faithful, "grade_faithful", grader)
    run_eval.run("r1", "v1", results_dir=tmp_path / "results")
    assert honesty_cell(tmp_path) == "1.00"


def test_page_without_golden_file_is_previewed_with_empty_text(tmp_path, monkeypatch):
    seen = {}

    def spy(url, text):
        seen[url] = text
        return ok_preview(url, text)

    monkeypatch.setattr(save, "preview", spy)
    run_eval.run("r1", "v1", results_dir=tmp_path / "results")
    with_golden = {p.stem for p in run_eval.GOLDEN_DIR.glob("*.txt")}
    pages = run_eval.json.loads(run_eval.PAGES_PATH.read_text(encoding="utf-8"))
    missing = [p["url"] for p in pages if p["id"] not in with_golden]
    assert len(missing) == UNREADABLE
    assert all(seen[url] == "" for url in missing)


def test_every_page_honest_scores_one(tmp_path, capsys):
    run_eval.run("r1", "v1", results_dir=tmp_path / "results")
    out = capsys.readouterr().out
    assert f"Honesty: 1.00 ({PAGE_COUNT}/{PAGE_COUNT} pages honest" in out
    assert honesty_cell(tmp_path) == "1.00"
