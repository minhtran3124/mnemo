---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-04
---

# 0007. Boundary: ci.yml is outside the allowed file set

## Context

Finding F3 says '|| [ $? -eq 5 ]' in .github/workflows/ci.yml:25 treats pytest no-tests-collected as a pass, although tests/test_pre_commit.py now exists. The fix is to remove that tolerance in ci.yml.

## Options

- Edit ci.yml anyway
- Skip and flag the boundary for the owner

## Decision

Skip and flag the boundary. No file was changed.

## Why

The file list for tickets #10 and #13 does not name .github/workflows/ci.yml, and the rules say a fix touching a file outside that set must change nothing.

## Consequences

CI still passes if pytest collects no tests. The tolerance should be removed in a ticket that owns ci.yml.

## How to reverse

Add ci.yml to a ticket's file list and rerun this fix. The change is to make the Tests step 'uv run pytest -q'.
