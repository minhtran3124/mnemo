---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-06
---

# 0010. Boundary: F7 fix needs save.py and tests/test_save_preview.py, outside ticket #86 files

## Context

save.preview() picks the GitHub text floor by hostname (github.com) with a magic string, while save() uses fetcher result.source, which is 'github' only for repo URLs (fetcher.github.parse_repo). Non-repo github.com URLs get the GitHub floor in preview but the HTML floor in save().

## Options

- Skip: leave save.py unchanged, as it is outside the ticket's file set
- Edit save.py and tests/test_save_preview.py anyway

## Decision

Skip and change nothing

## Why

The boundary lists only evals/run_eval.py, tests/test_run_eval.py, evals/results/.gitkeep, docs/process/eval-process.md and evals/README.md. save.py and tests/test_save_preview.py are not named, so the rule forces a skip.

## Consequences

preview() can disagree with save() for non-repo github.com URLs. A follow-up ticket should make preview use fetcher.parse_repo(url) to choose the source, and _floor_for with the 'github' or 'web' constants, so both paths share one rule.

## How to reverse

Not applicable, nothing was changed.
