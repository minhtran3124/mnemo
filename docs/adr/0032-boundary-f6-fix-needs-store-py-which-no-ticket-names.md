---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0032. Boundary: F6 fix needs store.py, which no ticket names

## Context

F6 says one torn line in chat.jsonl makes every chat read and append raise StoreError. The cause is in store.py: _append_line is a buffered write that is not atomic, and _read_lines raises on any non-JSON line. The files named by tickets #37, #38 and #39 are server.py, intent.py, the listed tests and docs, and the web files. store.py is not among them.

## Options

- Edit store.py anyway
- Skip and flag the boundary
- Work around it in server.py by catching StoreError

## Decision

Skip and flag the boundary. No files changed, nothing pushed.

## Why

The file-set rule says a fix touching a file outside the set changes nothing. A server.py workaround would hide the storage fault, and the project says all storage goes through store.py.

## Consequences

F6 stays open. A later ticket that names store.py and tests/test_store.py needs to cover it. The fix would write each line with one os.write on an O_APPEND fd. It would add a newline first if the file does not end in one. It would skip or repair an unterminated final line on read.

## How to reverse

Add store.py and tests/test_store.py to a ticket's file list and rerun the fix stage for F6.
