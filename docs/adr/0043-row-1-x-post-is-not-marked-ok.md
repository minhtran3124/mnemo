---
ticket: 43
stage: implement
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: implement)
date: 2026-11-05
---

# 0043. Row 1 (X post) is not marked ok

## Context

The ticket defines ok for the X post as saved link only with a null summary. In this run the app fetched the post fully (about 18k chars) and wrote a faithful summary, so the unreadable case did not occur.

## Options

- Write ok anyway to reach the count of 5
- Mark the row differs and leave the count at 4
- Replace the X link with another unreadable link in the test set

## Decision

Mark row 1 as differs, record the unreadable and paste path with a Slack stand-in link, and keep the count at 4.

## Why

The task says never to write ok for a row that was not verified. Changing the test set is outside this ticket's files.

## Consequences

The verify command prints 4, not 5, so AC1 is not met. The owner must choose an unreadable link for row 1 of the Phase 1 test set (docs/reference/sample-links.md) and re-run it.

## How to reverse

Replace row 1 with a link that really fails to read, re-run it, and set its result to ok.
