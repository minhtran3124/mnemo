---
ticket: 10
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-04
---

# 0003. Boundary: ci.yml pytest exit-5 tolerance is outside ticket #10 files

## Context

Finding F2 says CI still accepts pytest exit code 5 (no tests collected) even though this PR adds tests/test_config.py. The fix is to change the Tests step in .github/workflows/ci.yml to plain 'uv run pytest -q'. Ticket #10 names only config.py, tests/test_config.py, pyproject.toml, .env.example, docs/reference/api-notes.md and docs/product/tech-stack.md.

## Options

- Skip and flag for the owner or a CI ticket
- Edit ci.yml anyway

## Decision

Skip; make no change to ci.yml.

## Why

The boundary rule forbids touching files outside the ticket's named set. No test in the allowed files could fail without this fix, since the problem is in the workflow file.

## Consequences

CI keeps tolerating exit code 5 until someone removes it. Collection failures that produce zero tests would pass silently.

## How to reverse

Replace the Tests step run line in .github/workflows/ci.yml with 'uv run pytest -q' in a ticket that names that file.
