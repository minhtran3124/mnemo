"""Score the golden pages and log the run.

Run from the repo root:
    uv run python -m evals.run_eval --run-id <id> --prompt-version <name>

The eval never calls the network for page text: a page with no golden file is
previewed with the text "" and saved link only, so scores do not depend on
today's web content.
Each page goes through `save.preview` (nothing is written to data/), then the
code graders and, for readable pages, the faithful-summary grader. Three scores
are printed side by side and never averaged. One row is appended to
evals/results/runs.csv after the whole loop, so a stopped run writes no row.
"""

import argparse
import csv
import json
import sys
from contextlib import contextmanager
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


class _CountingMessages:
    """Wrap sdk.messages so every response's usage is counted, even one that fails later."""

    def __init__(self, messages, total: list[int]):
        self._messages = messages
        self._total = total

    def parse(self, **kwargs):
        response = self._messages.parse(**kwargs)
        self._total[0] += response.usage.input_tokens + response.usage.output_tokens
        return response


class _CountingSdk:
    def __init__(self, sdk, total: list[int]):
        self.messages = _CountingMessages(sdk.messages, total)


@contextmanager
def _counting_sdk():
    """Patch client._get_client so every SDK response's usage lands in the yielded total."""
    original = client._get_client
    total = [0]
    client._get_client = lambda: _CountingSdk(original(), total)
    try:
        yield total
    finally:
        client._get_client = original


def _preview_counting(url: str, text: str | None) -> tuple[dict, int]:
    """Run save.preview and return the record and the tokens its Claude calls used.

    Counts at the SDK response, so a billed call that client.py then rejects
    (refusal, max_tokens, no parsed output) and save.py retries is still counted.
    """
    with _counting_sdk() as total:
        record = save.preview(url, text)
    return record, total[0]


def _grade_counting(
    text: str, summary: str, key_facts: list[str]
) -> tuple[faithful.FaithfulResult | None, int]:
    """Grade with retry and return the result and every token the grader calls billed.

    Counts at the SDK response, so a call rejected as invalid output, or a
    grade that ends as grader_failed, is still counted.
    """
    with _counting_sdk() as total:
        result = _grade_with_retry(text, summary, key_facts)
    return result, total[0]


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


def _grade_with_retry(
    text: str, summary: str, key_facts: list[str]
) -> faithful.FaithfulResult | None:
    """Grade once, retry once on a transient API error, like save._summarise.

    None means the grader never answered, so the page is reported as not scored.
    Permanent errors (bad key, non-transient 4xx) propagate.
    """
    for attempt in range(1, save.ATTEMPTS + 1):
        try:
            return faithful.grade_faithful(text, summary, key_facts)
        except anthropic.APIError as err:
            if save.is_permanent_error(err):
                raise
            if attempt == save.ATTEMPTS:
                return None
    return None


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
    honest_ok = unreadable_ok = unreadable_total = 0
    faith_ok = 0
    # Per group [passed, total] for save quality, so a gain on the tuning pages
    # that does not reach the held-out pages shows in the log.
    split = {True: [0, 0], False: [0, 0]}

    for page in pages:
        page_id = page["id"]
        entry = expected[page_id]
        golden_file = GOLDEN_DIR / f"{page_id}.txt"
        text = golden_file.read_text(encoding="utf-8") if golden_file.exists() else ""
        record, used = _preview_counting(page["url"], text)
        tokens += used
        grades = graders.grade_record(record, asdict(entry))

        result = None
        scored = False
        faith_candidate = (
            entry.expect == "ok"
            and record["page_status"] == "ok"
            and record["summary"] is not None
            and text
        )
        if faith_candidate:
            result, used = _grade_counting(
                text, record["summary"], list(entry.key_facts)
            )
            tokens += used
            if result is not None:
                scored = not result.grader_failed
            if not scored:
                not_scored.append(page_id)
        # A readable page is honest only when it was scored with 0 unsupported
        # statements. A page saved link only, with no golden text, or that the
        # grader could not score is named in notes and counts as not honest.
        readable_honest = scored and result.unsupported_count == 0
        faith_ok += int(readable_honest)

        if entry.expect == "ok":
            save_total += 1
            page_ok = int(
                record["page_status"] == "ok"
                and all(grades[name].passed for name in SAVE_CHECKS)
            )
            save_ok += page_ok
            split[entry.held_out][0] += page_ok
            split[entry.held_out][1] += 1
            overlaps.append(grades["tag_overlap"].score or 0.0)
        else:
            unreadable_total += 1
            unreadable_ok += int(grades["honest_failure"].passed)

        honest_ok += int(
            grades["honest_failure"].passed if entry.expect != "ok" else readable_honest
        )

        cells = [
            f"{name}: {'PASS' if grade.passed else 'FAIL'} ({grade.reason})"
            for name, grade in grades.items()
        ]
        cells.append(f"faithful: {_faithful_cell(result, scored)}")
        table.append(f"{page_id} | {entry.expect} | " + " | ".join(cells))

    save_quality = _rate(save_ok, save_total)
    overlap = sum(overlaps) / len(overlaps) if overlaps else None
    honesty = _rate(honest_ok, len(pages))
    readable_total = len(pages) - unreadable_total

    print(
        f"Save quality: {_fmt(save_quality)} ({save_ok}/{save_total} pass, "
        f"mean tag overlap {_fmt(overlap)})"
    )
    print(
        f"Honesty: {_fmt(honesty)} "
        f"({honest_ok}/{len(pages)} pages honest: "
        f"{unreadable_ok}/{unreadable_total} unreadable pages with a null summary, "
        f"{faith_ok}/{readable_total} readable pages with 0 unsupported statements)"
    )
    held_ok, held_total = split[True]
    tune_ok, tune_total = split[False]
    print(
        f"Save quality held-out: {_fmt(_rate(held_ok, held_total))} "
        f"({held_ok}/{held_total} pass) | "
        f"tuning: {_fmt(_rate(tune_ok, tune_total))} ({tune_ok}/{tune_total} pass)"
    )
    print("Find rate: - (available from phase 4)")
    print(f"Tokens used: {tokens}")
    print("\n".join(table))

    # The honesty column holds the share of all pages that are honest; the count
    # of readable pages with 0 unsupported statements is logged here.
    notes = [f"0 unsupported: {faith_ok}"]
    if not_scored:
        notes.append(f"not scored: {', '.join(not_scored)}")

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
                "; ".join(notes),
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
