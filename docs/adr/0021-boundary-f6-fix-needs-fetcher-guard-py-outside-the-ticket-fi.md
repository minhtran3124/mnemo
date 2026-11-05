---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0021. Boundary: F6 fix needs fetcher/guard.py, outside the ticket file sets

## Context

Finding F6 says check_host in fetcher/guard.py calls blocking socket.getaddrinfo with no timeout, so the per-attempt time cap does not cover DNS. The union of files named by tickets #32, #33 and #34 is save.py, prompts/save_system.txt, server.py, web/*, tests/test_save.py, tests/test_bookmarks_api.py, tests/test_web_assets.py and some docs. fetcher/guard.py and tests/test_fetcher.py are not in it.

## Options

- Skip and flag as a boundary issue
- Edit fetcher/guard.py anyway

## Decision

Skip and flag as a boundary issue

## Why

The run rules say a fix that touches a file outside the allowed set must change nothing and return skipped.

## Consequences

The DNS timeout gap stays open until a ticket that owns fetcher/guard.py (the fetcher ticket) takes it. A likely fix is to run resolve in a thread with a deadline and return 'could not look up the host' on timeout.

## How to reverse

Add fetcher/guard.py and tests/test_fetcher.py to a ticket's file set and rerun the fix stage.
