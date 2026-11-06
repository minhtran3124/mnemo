---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-06
---

# 0009. Boundary: F5 fix needs evals/faithful.py, which ticket #86 does not name

## Context

Finding F5 says _message in evals/faithful.py wraps page text and summary in <page>/<summary> tags without escaping, so crafted text can close the wrapper early. The ticket's allowed files are evals/run_eval.py, tests/test_run_eval.py, evals/results/.gitkeep, docs/process/eval-process.md and evals/README.md.

## Options

- Edit evals/faithful.py and add a test in a file outside the list
- Skip and flag the boundary

## Decision

Skip. Change nothing and flag the boundary.

## Why

The fix has to be made in evals/faithful.py (and its test). Neither file is on the ticket's list, and the rule says a fix outside the set must be skipped.

## Consequences

The grader still lacks escaping. A later ticket that owns evals/faithful.py must fix it.

## How to reverse

Add evals/faithful.py and its test file to a ticket's file set, then apply the same escaping that save._summarise uses.
