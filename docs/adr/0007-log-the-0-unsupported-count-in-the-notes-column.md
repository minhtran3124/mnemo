---
ticket: run
stage: intent-fix
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: intent-fix)
date: 2026-11-06
---

# 0007. Log the 0-unsupported count in the notes column

## Context

The ticket asks for two honesty measures (honest-failure pass rate and count of pages with 0 unsupported statements) but runs.csv has exactly eight fixed columns, none for the count.

## Options

- Keep eight columns; honesty = honest-failure rate, count in notes as '0 unsupported: N'
- Add a ninth column for the count
- Encode both numbers in the honesty cell

## Decision

Keep eight columns; honesty holds the honest-failure pass rate and notes starts with '0 unsupported: N' followed by any 'not scored: ...' list.

## Why

Adding a column would change the logged contract and the ticket says eight columns; a combined cell would break numeric parsing.

## Consequences

Anything reading notes now sees a leading '0 unsupported: N' entry; docs/process/eval-process.md updated to match.

## How to reverse

Add a dedicated column to COLUMNS and the doc table, and stop writing the count into notes.
