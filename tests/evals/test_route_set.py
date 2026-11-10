"""The Route set and the folder score (F-03, D-005)."""

import csv
import json
import re
from pathlib import Path

from evals import faithful, run_eval
from mnemo.core import client, config, store
from mnemo.save import pipeline as save

ROOT = Path(__file__).resolve().parents[2]
ROUTE_DOC = ROOT / "docs" / "feature-specs" / "test-cases" / "route-set.md"
PAGES = json.loads((ROOT / "evals" / "pages.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((ROOT / "evals" / "expected.json").read_text(encoding="utf-8"))


def route_rows() -> list[list[str]]:
    text = ROUTE_DOC.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        if re.match(r"^\| R-\d\d \|", line):
            rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def test_route_doc_has_15_drafts_with_an_allowed_folder():
    rows = route_rows()
    assert len(rows) == 15
    for row in rows:
        assert row[5] == "yes"
        assert config.is_allowed_folder(row[4])
    by_page = {entry["id"]: entry for entry in EXPECTED}
    for row in rows:
        page_id = row[1]
        expected = by_page[page_id]
        assert expected["expected_type"] == row[3]
        assert expected["expected_folder"] == row[4]
    assert [page["id"] for page in PAGES] == [row[1] for row in rows]


def test_folder_score_counts_a_made_up_name_as_a_miss():
    assert run_eval.folder_match("Learning", "Learning") is True
    assert run_eval.folder_match(None, "Unsorted") is True
    assert run_eval.folder_match("Unsorted", "Unsorted") is True
    assert run_eval.folder_match("Archive", "Unsorted") is False
    assert run_eval.folder_match("Archive", "Learning") is False
    assert run_eval.folder_match("learning", "Learning") is False


def test_old_rows_get_an_empty_folder_score(tmp_path):
    path = tmp_path / "runs.csv"
    path.write_text(
        "run_id,prompt_version,model,save_quality,honesty,find_rate,"
        "tokens_used,notes\n"
        "old,save_v1,claude-haiku-5-5,0.92,1.00,,120,note\n",
        encoding="utf-8",
    )

    run_eval._migrate_runs(path)

    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["run_id"] == "old"
    assert rows[0]["folder_score"] == ""
    assert rows[0]["tokens_used"] == "120"
    assert "folder_score" in run_eval.COLUMNS


def test_eval_prints_and_appends_the_folder_score(tmp_path, monkeypatch, capsys):
    def fake_preview(url, text, folder_choice=None, prompt_version=None):
        chosen = "Work" if url == PAGES[0]["url"] else config.UNSORTED
        if folder_choice is not None:
            folder_choice.append(chosen)
        return save._link_only_fields(url, url)

    monkeypatch.setattr(save, "preview", fake_preview)
    monkeypatch.setattr(
        faithful,
        "grade_faithful",
        lambda text, summary, facts: faithful.FaithfulResult(
            passed=True, unsupported_count=0, usage=client.Usage(10, 5)
        ),
    )
    monkeypatch.setattr(store, "DATA_DIR", tmp_path / "data")
    results = tmp_path / "results"

    run_eval.run("r-folder", "save_v1", results_dir=results)

    out = capsys.readouterr().out
    assert "Folder choice: " in out
    with (results / "runs.csv").open(encoding="utf-8", newline="") as handle:
        row = next(iter(csv.DictReader(handle)))
    assert row["folder_score"] == f"{4 / 15:.2f}"
