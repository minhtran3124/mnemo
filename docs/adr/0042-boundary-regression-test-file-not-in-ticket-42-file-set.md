---
ticket: 42
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0042. Boundary: regression test file not in ticket #42 file set

## Context

F4 fix replaces the hard-coded 1.375rem in the phone-width .panel legend h2 rule with a --h2-panel-size token (same rendered value). The required failing-without-fix test belongs in tests/test_web_assets.py, which ticket #42 does not list.

## Options

- Skip the fix
- Add the test to tests/test_web_assets.py anyway
- Fix CSS without a test

## Decision

Skip the fix and change nothing

## Why

The file-set rule says a test file is in bounds only when listed; the fix needs a test, so it cannot be done within the boundary.

## Consequences

F4 stays open. The fix was verified locally (15 tests pass, ruff clean) before reverting, so it can be re-applied once tests/test_web_assets.py is allowed.

## How to reverse

Allow tests/test_web_assets.py for ticket #42 and re-run the fix stage.
