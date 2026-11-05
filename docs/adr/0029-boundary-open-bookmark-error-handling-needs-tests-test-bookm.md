---
ticket: run
stage: fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0029. Boundary: open_bookmark error handling needs tests/test_bookmarks_api.py

## Context

F2: open_bookmark in server.py does get_bookmark then update_bookmark without catching store.NotFound or store.StoreError. The route is already under _write_lock, so the race is narrow, but a corrupt bookmarks.json or an error from update_bookmark still gives an unhandled 500 outside the documented JSON error shape. The existing open and delete route tests live in tests/test_bookmarks_api.py, which is not in any ticket's file list.

## Options

- Put the regression test in tests/test_bookmarks_api.py (outside the boundary)
- Put it in a listed file such as tests/test_note.py or tests/test_chat_history.py (unrelated topic)
- Skip and report the boundary conflict

## Decision

Skip and report the boundary conflict.

## Why

The instructions say a fix that touches a file outside the named set must change nothing. A test is required, and the natural home for it is unlisted. Using an unrelated listed file would only dodge the boundary.

## Consequences

F2 stays open. The fix is ready and was checked locally, but it was not committed. In server.py, wrap the get and update in try/except. Map store.NotFound to _not_found(bookmark_id) and store.StoreError to error_response(500, 'storage_error', ...). Two tests in tests/test_bookmarks_api.py: monkeypatch store.update_bookmark to raise NotFound and expect 404 bookmark_not_found; write a corrupt bookmarks.json and expect 500 storage_error. Both failed without the fix, and all 10 tests passed with it. ruff check and ruff format --check were clean.

## How to reverse

Add tests/test_bookmarks_api.py to a ticket's file list and rerun this fix stage.
