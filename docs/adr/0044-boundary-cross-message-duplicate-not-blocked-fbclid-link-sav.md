---
ticket: 43
stage: implement
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: implement)
date: 2026-11-05
---

# 0044. Boundary: cross-message duplicate not blocked (fbclid link saved as new bookmark id 6)

## Context

The same link with ?fbclid=abc gives the same url_clean as the first save, as required. It was still saved as a second bookmark. The plan said no duplicate should be created. chat-and-intent.md lists a 'You saved this already' reply for an exact duplicate; only same-message duplicates are dropped today.

## Options

- Fix save/server to detect duplicates (outside this ticket's files)
- Record it as an open question in the results file

## Decision

Record it as an open question in the results file and make no code change.

## Why

The ticket allows only docs/manual-testing/phase1-links-check.md and docs/README.md, and the eval and duplicate work is another ticket or phase.

## Consequences

Duplicate saves are possible until a duplicate check is built. The owner may want an issue for it.

## How to reverse

n/a, doc-only note.
