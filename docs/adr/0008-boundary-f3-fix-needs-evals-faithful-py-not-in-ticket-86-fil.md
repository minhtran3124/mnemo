---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-06
---

# 0008. Boundary: F3 fix needs evals/faithful.py, not in ticket #86 file set

## Context

F3 says key_fact_results from the faithful grader is never length-checked or used in a score, so a summary omitting every key fact passes. The code is in evals/faithful.py (grade_faithful), which belongs to the grader ticket. Ticket #86 names only evals/run_eval.py, tests/test_run_eval.py, evals/results/.gitkeep, docs/process/eval-process.md and evals/README.md.

## Options

- Edit evals/faithful.py and tests/test_faithful_grader.py (outside the boundary)
- Patch around it in evals/run_eval.py (duplicates grader logic, wrong layer)
- Skip and flag for a ticket that owns faithful.py

## Decision

Skip and flag for the ticket that owns faithful.py.

## Why

The instructions say a fix touching a file outside the set changes nothing. Scoring key facts also changes the pass/fail contract of grade_faithful, which other tickets use.

## Consequences

F3 stays unfixed on this branch. Someone must decide whether key facts count toward the faithful pass, and add a length check against the number of key facts.

## How to reverse

Nothing was changed.
