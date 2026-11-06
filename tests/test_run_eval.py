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


def test_honesty_column_is_failure_rate_and_unsupported_count_is_logged(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        faithful,
        "grade_faithful",
        lambda text, summary, facts: faithful.FaithfulResult(
            passed=False, unsupported_count=2, usage=client.Usage(10, 5)
        ),
    )
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    row = dict(zip(*rows(results / "runs.csv"), strict=True))
    assert row["honesty"] == "0.20"
    assert row["notes"] == "0 unsupported: 0"


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

    class Usage:
        input_tokens = 100
        output_tokens = 20

    class Response:
        usage = Usage()
        stop_reason = "end_turn"
        parsed_output = save.SaveOutput(
            title="A page",
            type="article",
            summary="A short summary.",
            tags=["a", "b", "c"],
            reason="Useful.",
        )

    class Messages:
        def parse(self, **kwargs):
            calls.append(1)
            return Response()

    class Sdk:
        messages = Messages()

    monkeypatch.setattr(save, "preview", REAL_PREVIEW)
    monkeypatch.setattr(client, "_get_client", lambda: Sdk())
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    row = rows(results / "runs.csv")[1]
    assert calls
    assert int(row[6]) == len(calls) * (100 + 20)
    assert not (tmp_path / "data").exists() or not list((tmp_path / "data").rglob("*"))


def test_unreadable_page_without_golden_file_never_hits_the_network(
    tmp_path, monkeypatch, capsys
):
    calls = []

    def live_fetch(url):
        calls.append(url)
        return fetcher.FetchOk("long text " * 200, "web")

    monkeypatch.setattr(fetcher, "fetch", live_fetch)
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    out = capsys.readouterr().out
    assert calls == []
    assert "3/3 unreadable pages with a null summary" in out


def test_unscored_readable_pages_are_not_scored_and_named_in_notes(
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
    assert "0/12 readable pages with 0 unsupported statements or a null summary" in out
    row = dict(zip(*rows(results / "runs.csv"), strict=True))
    assert float(row["honesty"]) == 0.2
    assert row["notes"].startswith("0 unsupported: 0; not scored:")


def test_tokens_include_billed_calls_rejected_as_invalid_output(tmp_path, monkeypatch):
    """A reply cut off at max_tokens is billed even though the retry replaces it."""
    out = save.SaveOutput(
        title="A page",
        type="article",
        summary="A short summary.",
        tags=["a", "b", "c"],
        reason="Useful.",
    )
    calls = []

    class Usage:
        input_tokens = 100
        output_tokens = 20

    class Response:
        usage = Usage()

        def __init__(self, stop_reason, parsed):
            self.stop_reason = stop_reason
            self.parsed_output = parsed

    class Messages:
        def parse(self, **kwargs):
            calls.append(1)
            if len(calls) % 2 == 1:
                return Response("max_tokens", None)
            return Response("end_turn", out)

    class Sdk:
        messages = Messages()

    monkeypatch.setattr(save, "preview", REAL_PREVIEW)
    monkeypatch.setattr(client, "_get_client", lambda: Sdk())
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    row = rows(results / "runs.csv")[1]
    assert len(calls) % 2 == 0 and calls
    assert int(row[6]) == len(calls) * 120


def test_transient_grader_error_is_retried_once_then_scored(tmp_path, monkeypatch):
    import anthropic
    import httpx2 as httpx

    calls = []

    def flaky(text, summary, facts):
        calls.append(1)
        if len(calls) % 2 == 1:
            raise anthropic.APIConnectionError(
                request=httpx.Request("POST", "https://x.test")
            )
        return faithful.FaithfulResult(
            passed=True, unsupported_count=0, usage=client.Usage(10, 5)
        )

    monkeypatch.setattr(faithful, "grade_faithful", flaky)
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    row = dict(zip(*rows(results / "runs.csv"), strict=True))
    assert "not scored" not in row["notes"]
    assert len(calls) % 2 == 0 and calls


def test_held_out_save_quality_reported_separately(tmp_path, capsys, monkeypatch):
    held = {
        entry.id
        for entry in run_eval.golden.load_expected(run_eval.EXPECTED_PATH)
        if entry.held_out and entry.expect == "ok"
    }
    real = run_eval.graders.grade_record

    def failing_on_held_out(record, expected):
        grades = real(record, expected)
        if expected["id"] in held:
            grades["schema"] = run_eval.graders.GradeResult(False, "forced")
        return grades

    monkeypatch.setattr(run_eval.graders, "grade_record", failing_on_held_out)
    run_eval.run("r1", "v1", results_dir=tmp_path / "results")
    out = capsys.readouterr().out
    assert f"Save quality held-out: 0.00 (0/{len(held)} pass)" in out
    assert "| tuning: " in out


def test_link_only_save_of_readable_page_is_honest_and_not_unscored(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(
        save, "preview", lambda url, text: save._link_only_fields(url, url)
    )
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    out = capsys.readouterr().out
    assert "12/12 readable pages with 0 unsupported statements or a null summary" in out
    row = dict(zip(*rows(results / "runs.csv"), strict=True))
    assert float(row["honesty"]) == 1.0
    assert row["notes"] == "0 unsupported: 0"


def test_eval_process_doc_matches_honesty_columns():
    doc = (run_eval.EVALS_DIR.parent / "docs/process/eval-process.md").read_text(
        encoding="utf-8"
    )
    assert "share of all pages" in doc
    assert "0 unsupported: N" in doc


def test_tokens_include_grader_calls_rejected_as_invalid_output(tmp_path, monkeypatch):
    """A grader reply that fails validation is billed, so it counts in tokens_used."""
    monkeypatch.undo()
    monkeypatch.setattr(store, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(save, "preview", fake_preview)
    monkeypatch.setattr(
        fetcher, "fetch", lambda url: fetcher.FetchFail("test: no network")
    )
    calls = []

    class Usage:
        input_tokens = 100
        output_tokens = 20

    class Response:
        usage = Usage()

        def __init__(self, stop_reason, parsed):
            self.stop_reason = stop_reason
            self.parsed_output = parsed

    class Messages:
        def parse(self, **kwargs):
            calls.append(1)
            if len(calls) % 2 == 1:
                return Response("max_tokens", None)
            return Response(
                "end_turn", faithful.FaithfulOutput(unsupported=[], key_fact_results=[])
            )

    class Sdk:
        messages = Messages()

    monkeypatch.setattr(client, "_get_client", lambda: Sdk())
    results = tmp_path / "results"
    run_eval.run("r1", "v1", results_dir=results)
    row = rows(results / "runs.csv")[1]
    assert len(calls) % 2 == 0 and calls
    assert int(row[6]) == len(calls) * 120
