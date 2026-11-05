---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0046. Boundary: F2 fix touches server.py, urlclean.py and tests outside the ticket file set

## Context

Finding F2: POST /api/chat with 'http://[abc' makes urlsplit raise ValueError in urlclean.clean_url. It is called at server.py:354 outside the try block, and again inside save.save, so guarding only the server line would still give a 500. The finding is real and I reproduced that intent.find_links returns ['http://[abc']. The tickets #41, #42 and #43 name only docs, web/ and CSS files.

## Options

- Skip and flag the boundary
- Edit server.py, urlclean.py and add a test in tests/ anyway

## Decision

Skip and flag the boundary

## Why

The run rules say a fix that touches a file outside the named set must change nothing and return skipped. The listed files exclude server.py, urlclean.py and every file under tests/.

## Consequences

The malformed bracketed-host 500 remains until a ticket that covers server.py and urlclean.py picks it up. The suggested fix is to make clean_url return the input unchanged on ValueError, which covers both call sites, and add a chat API test for 'http://[abc'.

## How to reverse

Widen the file set to include urlclean.py, server.py and tests/test_chat_api.py and rerun the fix stage.
