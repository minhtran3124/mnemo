---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0050. Boundary: F6 fix touches intent.py and tests/test_intent.py, outside the ticket file sets

## Context

Finding F6 says int(raw_id) in parse_note (intent.py:53) raises ValueError on a digit string over 4300 digits, which gives a 500. The fix is to bound the id with \d{1,9} in the _NOTE regex, or to catch the error. The tickets in this run (#41, #42, #43) name only web/css, web/html, docs/manual-testing, docs/feature-specs/ui-reference.md, docs/design/v3-mockup/README.md and docs/README.md.

## Options

- Skip and flag the boundary
- Edit intent.py and tests/test_intent.py anyway

## Decision

Skip. Change nothing and flag the boundary.

## Why

The rules say a fix that touches a file outside the named set must change nothing and return skipped.

## Consequences

F6 stays open. An oversized note id will still raise ValueError, and the server will return a 500, until another ticket covers intent.py.

## How to reverse

Add intent.py and tests/test_intent.py to a ticket's file list and re-run this fix. The change is to use \d{1,9} for the id group in _NOTE, plus a test for a very long digit id.
