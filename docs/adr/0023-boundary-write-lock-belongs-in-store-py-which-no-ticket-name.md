---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0023. Boundary: write lock belongs in store.py, which no ticket names

## Context

F1 says the process-local threading.Lock in server.py:23 does not cover store.py add/update/delete or the separate MCP process, so the lock must live in store.py. The file sets of tickets #32, #33 and #34 do not include store.py (or its tests or docs/feature-specs/storage.md).

## Options

- Edit store.py anyway to add the lock
- Skip and flag the boundary for a store.py ticket

## Decision

Skip and flag the boundary. No file was changed and nothing was pushed.

## Why

The run rules say a fix that touches a file outside the allowed set must change nothing. A correct fix also needs a cross-process lock in store.py (for example an fcntl file lock), which changes how all bookmark storage is written. That is a public storage contract.

## Consequences

Lost updates remain possible between the HTTP server and the MCP process until a ticket covers store.py locking.

## How to reverse

Add store.py, its tests and docs/feature-specs/storage.md to a ticket's file set, then rerun this fix.
