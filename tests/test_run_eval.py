"""The eval runner, with Claude mocked (no network)."""

import csv
import json

import pytest

import client
import config
import fetcher
import save
import store
from evals import faithful, run_eval

REAL_PREVIEW = save.preview
PAGES = json.loads(run_eval.PAGES_PATH.read_text(encoding="utf-8"))
ARGS = ["--run-id", "r1", "--prompt-version", "save_v1"]


def fake_preview(url, text):
    if text is None:
        return save._link_only_fields(url, url)
    out = save.SaveOutput(
        title="A page",
        type="article",
        summary="A short summary.",
        tags=["a", "b", "c"],
        reason="Useful.",
    )
    return save._ok_fields(url, url, out)


@pytest.fixture(autouse=True)
def fakes(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(save, "preview", fake_preview)
    monkeypatch.setattr(
        faithful,
        "grade_faithful",
        lambda text, summary, facts: faithful.FaithfulResult(
            passed=True, unsupported_count=0, usage=client.Usage(10, 5)
        ),
    )
    monkeypatch.setattr(
        fetcher, "fetch", lambda url: fetcher.FetchFail("test: no network")
    )
    monkeypatch.setattr(run_eval, "RESULTS_DIR", tmp_path / "results")


def rows(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def test_prints_three_separate_scores_and_no_average(tmp_path, capsys):
    assert run_eval.run("r1", "v1", results_dir=tmp_path / "results") == 0
    out = capsys.readouterr().out
    assert "Save quality: " in out
    assert "mean tag overlap" in out
    assert "Honesty: " in out
    assert "Find rate: - (available from phase 4)" in out
    assert not any(w in out.lower() for w in ("average", "combined", "overall"))


def test_run_appends_one_row_with_eight_columns(tmp_path):
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    table = rows(results / "runs.csv")
    assert table[0] == run_eval.COLUMNS
    assert len(table) == 2
    row = dict(zip(table[0], table[1], strict=True))
    assert row["find_rate"] == ""
    assert row["model"] == config.MODEL
    assert row["run_id"] == "r1"
    assert row["prompt_version"] == "v1"


def test_second_run_appends_and_keeps_first(tmp_path):
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    first = rows(results / "runs.csv")[1]
    run_eval.run("r2", "v1", results_dir=results)
    table = rows(results / "runs.csv")
    assert table.count(run_eval.COLUMNS) == 1
    assert len(table) == 3
    assert table[1] == first
    assert table[2][0] == "r2"


def test_draft_warning_printed(tmp_path, capsys):
    entries = json.loads(run_eval.EXPECTED_PATH.read_text(encoding="utf-8"))
    for entry in entries:
        entry["draft"] = False
    entries[0]["draft"] = True
    copy = tmp_path / "expected.json"
    copy.write_text(json.dumps(entries), encoding="utf-8")
    run_eval.run("r1", "v1", results_dir=tmp_path / "results", expected_path=copy)
    warnings = [
        line for line in capsys.readouterr().out.splitlines() if "WARNING" in line
    ]
    assert len(warnings) == 1
    assert "1 expected entries" in warnings[0]
    assert entries[0]["id"] in warnings[0]


def test_permanent_error_stops_run_and_writes_no_row(tmp_path, monkeypatch, capsys):
    def boom(url, text):
        raise client.MissingKey("no key")

    monkeypatch.setattr(save, "preview", boom)
    assert run_eval.main(ARGS) == 1
    assert "Run stopped" in capsys.readouterr().err
    assert not (tmp_path / "results" / "runs.csv").exists()


def test_data_dir_untouched(tmp_path, monkeypatch):
    calls = []

    def fake_parse(messages, output_format, system=None, **kwargs):
        calls.append(1)
        out = save.SaveOutput(
            title="A page",
            type="article",
            summary="A short summary.",
            tags=["a", "b", "c"],
            reason="Useful.",
        )
        return out, client.Usage(100, 20)

    monkeypatch.setattr(save, "preview", REAL_PREVIEW)
    monkeypatch.setattr(client, "parse_with_usage", fake_parse)
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    row = rows(results / "runs.csv")[1]
    assert calls
    assert int(row[6]) == len(calls) * (100 + 20) + len(calls) * (10 + 5)
    assert not (tmp_path / "data").exists() or not list((tmp_path / "data").rglob("*"))


def test_unreadable_page_that_now_reads_fails_honesty(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        fetcher, "fetch", lambda url: fetcher.FetchOk("long text " * 200, "web")
    )
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    out = capsys.readouterr().out
    assert "0/3 unreadable pages honest" in out
    row = dict(zip(*rows(results / "runs.csv"), strict=True))
    assert float(row["honesty"]) < 1.0


def test_unscored_readable_pages_count_as_honesty_failures(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(
        faithful,
        "grade_faithful",
        lambda text, summary, facts: faithful.FaithfulResult(
            passed=False,
            unsupported_count=0,
            usage=client.Usage(10, 5),
            grader_failed=True,
        ),
    )
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    out = capsys.readouterr().out
    assert "0/12 readable pages" in out
    row = dict(zip(*rows(results / "runs.csv"), strict=True))
    assert float(row["honesty"]) < 1.0
    assert row["notes"].startswith("not scored:")
