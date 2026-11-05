---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0017. Boundary: lock lives in server.py, not store.py

## Context

The race is in store's unlocked read-modify-write; add_bookmark and append_chat ids are also affected, but store.py is outside the allowed file set.

## Options

- Lock in store.py (out of boundary)
- Lock in server.py routes only

## Decision

Added a threading.Lock in server.py around open and delete. add_bookmark and append_chat paths (save.py, chat) are not covered by it.

## Why

Stays inside the allowed files; fixes the reported open_count loss.

## Consequences

Concurrent add/append_chat can still race. A store-level lock (storage.md open question) is needed to cover them.

## How to reverse

Remove the lock and move it into store.py.
