---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: review-fix)
date: 2026-11-06
---

# 0002. Skip F1: keep link-only saves of readable pages scored honest

## Context

evals/run_eval.py scores a readable page saved link only (summary None) as honest. docs/process/eval-process.md says this on purpose: nothing was invented, and the failure shows in save quality. Tests in tests/test_run_eval.py and tests/test_run_eval_honesty.py assert 15/15 for this case. The save-quality check for expect=ok pages already fails when page_status is not ok.

## Options

- Leave the metric as documented and change nothing
- Score a link-only save of a readable page as not honest, and rewrite the docs and three tests

## Decision

Leave the metric as documented and change nothing.

## Why

Making that save count as not honest redefines the Phase 2 honesty score. It would invert tests that state the intended behaviour, which looks like weakening them. It would also change the meaning of the baseline numbers already logged in runs.csv. The failure on readable pages is already caught by save quality. The finding concerns metric design, not a defect in the code.

## Consequences

The honesty score still cannot see a saver that fails on readable pages. Save quality is the number that exposes it.

## How to reverse

Change the elif record['summary'] is None branch in evals/run_eval.py to use scored_clean, then update the docs and the three tests that assert 15/15.
