---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0033. Boundary: F7 fix needs urlclean.py and tests/test_url_clean.py, outside the ticket file set

## Context

urlclean.py line 15 calls urlsplit(url) with no error handling, so 'http://[abc' raises ValueError. The allowed files are server.py, intent.py, tests/test_chat_history.py, tests/test_note.py, docs/feature-specs/chat-and-intent.md, docs/feature-specs/storage.md, web/bookmarks.html, web/js/view-switcher.js, web/css/bookmarks.css and tests/test_view_switcher.py.

## Options

- Skip and report the boundary
- Edit urlclean.py anyway
- Catch ValueError in server.py around clean_url

## Decision

Skip and report the boundary

## Why

The run's rules say a fix touching a file outside the named set changes nothing. A catch in server.py would leave clean_url itself unsafe for other callers.

## Consequences

The malformed-URL crash in clean_url stays until a ticket that names urlclean.py and tests/test_url_clean.py covers it.

## How to reverse

Add urlclean.py and tests/test_url_clean.py to a ticket's file set and rerun the fix: wrap urlsplit in try/except ValueError and return the original URL.
