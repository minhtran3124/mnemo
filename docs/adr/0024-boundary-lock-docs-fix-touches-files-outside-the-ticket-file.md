---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0024. Boundary: lock docs fix touches files outside the ticket file set

## Context

Finding F2 says storage.md (line 63 and the Open questions list), the store.py docstring (lines 7-8, 'No lock yet') and tech-stack.md (lines 107 and 116) still call concurrent writes an open question after the lock was added. The correct fix edits those three files.

## Options

- Edit the three files anyway
- Skip and report a boundary violation
- Add the files to the ticket file set

## Decision

Skip and report a boundary violation

## Why

The run's file set covers save.py, prompts/save_system.txt, tests/test_save.py, honest-failure.md, server.py, tests/test_bookmarks_api.py, server-api.md, the web/ files, frontend-ui.md and theming-and-design-tokens.md. store.py, storage.md and tech-stack.md are not listed, and a fix outside the set must change nothing.

## Consequences

The stale lock wording stays in storage.md, store.py and tech-stack.md until a ticket that owns those files is added or the set is widened.

## How to reverse

Widen the boundary to include store.py, docs/feature-specs/storage.md and docs/product/tech-stack.md, then rerun the fix stage.
