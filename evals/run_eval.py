"""Score the golden pages and log the run.

Run from the repo root:
    uv run python -m evals.run_eval --run-id <id> --prompt-version <name>

Each page goes through `save.preview` (nothing is written to data/), then the
code graders and, for readable pages, the faithful-summary grader. Three scores
are printed side by side and never averaged. One row is appended to
evals/results/runs.csv after the whole loop, so a stopped run writes no row.
"""

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path

import anthropic

import client
import config
import save
from evals import faithful, golden, graders

EVALS_DIR = Path(__file__).resolve().parent
PAGES_PATH = EVALS_DIR / "pages.json"
GOLDEN_DIR = EVALS_DIR / "golden"
EXPECTED_PATH = EVALS_DIR / "expected.json"
RESULTS_DIR = EVALS_DIR / "results"
COLUMNS = [
    "run_id",
    "prompt_version",
    "model",
    "save_quality",
    "honesty",
    "find_rate",
    "tokens_used",
    "notes",
]
SAVE_CHECKS = ("schema", "tags", "summary_length", "type_match")


def _preview_counting(url: str, text: str | None) -> tuple[dict, int]:
    """Run save.preview and return the record and the tokens its Claude calls used."""
    original = client.parse_with_usage
    total = [0]

    def counting(*args, **kwargs):
        parsed, usage = original(*args, **kwargs)
        total[0] += usage.input_tokens + usage.output_tokens
        return parsed, usage

    client.parse_with_usage = counting
    try:
        record = save.preview(url, text)
    finally:
        client.parse_with_usage = original
    return record, total[0]


def _rate(passed: int, total: int) -> float | None:
    return passed / total if total else None


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _faithful_cell(result: faithful.FaithfulResult | None, scored: bool) -> str:
    if result is None:
        return "-"
    if not scored:
        return "not scored"
    return "pass" if result.passed else f"fail ({result.unsupported_count} unsupported)"


def run(
    run_id: str,
    prompt_version: str,
    *,
    results_dir: Path | None = None,
    expected_path: Path | None = None,
) -> int:
    """Score every page, print the report and append one row to runs.csv."""
    results_dir = RESULTS_DIR if results_dir is None else results_dir
    expected_path = EXPECTED_PATH if expected_path is None else expected_path
    pages = json.loads(PAGES_PATH.read_text(encoding="utf-8"))
    entries = golden.load_expected(expected_path)
    expected = {entry.id: entry for entry in entries}
    if set(expected) != {page["id"] for page in pages}:
        raise ValueError("ids in pages.json and expected.json do not match")

    drafts = [entry.id for entry in entries if entry.draft]
    if drafts:
        print(
            f"WARNING: {len(drafts)} expected entries are still draft: "
            f"{', '.join(drafts)}"
        )

    tokens = 0
    not_scored: list[str] = []
    table: list[str] = []
    save_ok = save_total = 0
    overlaps: list[float] = []
    honest_ok = honest_total = 0
    faith_ok = faith_total = 0

    for page in pages:
        page_id = page["id"]
        entry = expected[page_id]
        golden_file = GOLDEN_DIR / f"{page_id}.txt"
        text = golden_file.read_text(encoding="utf-8") if golden_file.exists() else None
        record, used = _preview_counting(page["url"], text)
        tokens += used
        grades = graders.grade_record(record, asdict(entry))

        result = None
        scored = False
        if (
            entry.expect == "ok"
            and record["page_status"] == "ok"
            and record["summary"] is not None
            and text is not None
        ):
            try:
                result = faithful.grade_faithful(
                    text, record["summary"], list(entry.key_facts)
                )
            except anthropic.APIError as err:
                if save.is_permanent_error(err):
                    raise
            if result is not None:
                tokens += result.usage.input_tokens + result.usage.output_tokens
                scored = not result.grader_failed
            if not scored:
                not_scored.append(page_id)
            else:
                faith_total += 1
                faith_ok += 1 if result.unsupported_count == 0 else 0

        if entry.expect == "ok":
            save_total += 1
            save_ok += int(
                record["page_status"] == "ok"
                and all(grades[name].passed for name in SAVE_CHECKS)
            )
            overlaps.append(grades["tag_overlap"].score or 0.0)
        else:
            honest_total += 1
            honest_ok += int(grades["honest_failure"].passed)

        cells = [
            f"{name}: {'PASS' if grade.passed else 'FAIL'} ({grade.reason})"
            for name, grade in grades.items()
        ]
        cells.append(f"faithful: {_faithful_cell(result, scored)}")
        table.append(f"{page_id} | {entry.expect} | " + " | ".join(cells))

    save_quality = _rate(save_ok, save_total)
    overlap = sum(overlaps) / len(overlaps) if overlaps else None
    honesty = _rate(honest_ok + faith_ok, honest_total + faith_total)

    print(
        f"Save quality: {_fmt(save_quality)} ({save_ok}/{save_total} pass, "
        f"mean tag overlap {_fmt(overlap)})"
    )
    print(
        f"Honesty: {_fmt(honesty)} "
        f"({honest_ok}/{honest_total} unreadable pages honest, "
        f"{faith_ok}/{faith_total} readable pages with 0 unsupported statements)"
    )
    print("Find rate: - (available from phase 4)")
    print(f"Tokens used: {tokens}")
    print("\n".join(table))

    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / "runs.csv"
    new_file = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(COLUMNS)
        writer.writerow(
            [
                run_id,
                prompt_version,
                config.MODEL,
                "" if save_quality is None else _fmt(save_quality),
                "" if honesty is None else _fmt(honesty),
                "",
                tokens,
                f"not scored: {', '.join(not_scored)}" if not_scored else "",
            ]
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse the command line and run. A permanent API error stops with exit code 1."""
    parser = argparse.ArgumentParser(prog="python -m evals.run_eval")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--prompt-version", required=True)
    args = parser.parse_args(argv)
    try:
        return run(args.run_id, args.prompt_version)
    except (client.MissingKey, anthropic.APIError) as err:
        if not save.is_permanent_error(err):
            raise
        print(
            f"Run stopped: {type(err).__name__}: check ANTHROPIC_API_KEY and "
            "API access. No row written.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
