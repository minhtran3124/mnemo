---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0018. Boundary: F2 fix is in client.py, not in any ticket's file set

## Context

Finding F2: client.parse() calls sdk.messages.parse, which validates the JSON before stop_reason is checked. A refusal or a max_tokens cut-off therefore raises a pydantic ValidationError instead of the documented RuntimeError. The fix is to catch ValidationError around sdk.messages.parse in client.py and raise RuntimeError, plus a regression test in tests/test_client.py.

## Options

- Edit client.py and tests/test_client.py anyway
- Skip and flag the boundary so the orchestrator or owner can widen the file set

## Decision

Skip; make no changes.

## Why

Neither client.py nor tests/test_client.py is named by tickets #32, #33 or #34, and the run rules say a fix outside the set must change nothing.

## Consequences

The documented RuntimeError contract in client.parse stays broken on refusal or truncation until the file set is widened or a ticket covers client.py.

## How to reverse

Add client.py and tests/test_client.py to a ticket's file set and rerun the fix stage.
