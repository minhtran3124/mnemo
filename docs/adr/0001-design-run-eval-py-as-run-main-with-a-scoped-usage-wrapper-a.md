---
ticket: 86
stage: design
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: design)
date: 2026-11-06
---

# 0001. Design: run_eval.py as run()/main() with a scoped usage wrapper and post-loop CSV append

## Context

Ticket #86 needs one command that previews and grades the 15 golden pages, prints three separate scores, and appends one 8-column row to evals/results/runs.csv, without changing the merged modules #80-#85 and with the API mocked in tests.

## Options

- A: one module with run() and main(), a scoped client.parse_with_usage wrapper for save tokens, and the CSV row appended after the loop
- B: change save.preview to return usage
- C: count only grader tokens
- D: test through a subprocess

## Decision

Option A. run(run_id, prompt_version, *, results_dir, expected_path) -> int and main(argv) -> int. main maps permanent errors (MissingKey, non-transient APIStatusError) to one message and exit code 1. runs.csv is appended once after the loop with the header written only for a new file. Columns: run_id, prompt_version, model, save_quality, honesty, find_rate, tokens_used, notes.

## Why

It reuses every merged module unchanged, makes 'no row on permanent error' true by construction, and gives the tests a seam monkeypatch can reach.

## Consequences

Defines the runs.csv format (stored run-log data) that later phase-2 tickets read. tokens_used undercounts failed save attempts. The wrapper briefly replaces a module global.

## How to reverse

Delete evals/run_eval.py, tests/test_run_eval.py and evals/results/, and revert the run-log section of eval-process.md.
