---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0051. Boundary: F7 failed links need server.py and store.py, which no ticket names

## Context

Finding F7 is real. drawHistory in web/js/chat.js reads message.failed, but _record_exchange in server.py and store.append_chat never store the failed links, and /api/chat/history never returns them. Failed-link cards vanish after a reload.

## Options

- Store failed in chat.jsonl via store.append_chat and server._record_exchange, return it from /api/chat/history, add a test in tests/test_chat_history.py, update docs/feature-specs/storage.md
- Delete the dead message.failed branch in web/js/chat.js (the summary text line already survives a reload)
- Skip and report as a boundary violation

## Decision

Skipped. Nothing was changed.

## Why

Both real fixes touch files outside the union of the file lists for tickets #41, #42 and #43. Those are server.py, store.py, web/js/chat.js, tests/test_chat_history.py and docs/feature-specs/storage.md. The task rules say to change nothing and return skipped in that case.

## Consequences

Failed-link cards still disappear after a reload. The partial-failure summary line (for example '1 could not be saved.') is still shown. The drawHistory failed branch remains dead code until a ticket that names these files picks this up.

## How to reverse

Not applicable, since nothing changed. A later ticket that names server.py and store.py can store the failed urls on the app chat line and return them from /api/chat/history.
