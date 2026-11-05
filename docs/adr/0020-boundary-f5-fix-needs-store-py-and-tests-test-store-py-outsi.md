---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0020. Boundary: F5 fix needs store.py and tests/test_store.py, outside the ticket file sets

## Context

_append_line in store.py does not check for a trailing newline. A torn last line in chat.jsonl makes list_chat raise StoreError, and the next append glues a new record onto the partial text. Tickets #32, #33 and #34 do not name store.py or tests/test_store.py.

## Options

- Edit store.py and tests/test_store.py anyway
- Skip and flag the boundary

## Decision

Skipped. I tried a fix and confirmed it worked: _append_line repairs the tail first (finishes a whole last line, drops a torn one) and _read_lines ignores a torn last line. Two new tests failed without the fix and passed with it. I then reverted everything because the files are out of bounds.

## Why

The boundary rule says a fix touching a file outside the set must change nothing.

## Consequences

F5 stays open until a ticket that names store.py covers it.

## How to reverse

Add store.py and tests/test_store.py to a ticket's file set, then apply the tail repair in _append_line and torn-line tolerance in _read_lines.
