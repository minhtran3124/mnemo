---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0022. Boundary: docs/adr cleanup is outside every ticket's file set

## Context

Finding F9 reports 11 autopilot-generated docs/adr files, several stale, with real decisions missing from docs/process/decision-log.md. The ticket file sets for #32, #33 and #34 do not include docs/adr/* or docs/process/decision-log.md.

## Options

- Skip and flag the boundary
- Delete or edit the docs/adr files and decision-log.md anyway

## Decision

Skip and make no change.

## Why

The run rules say a fix touching a file outside the ticket file sets must change nothing and return skipped. A test that fails without the fix is also not meaningful for a docs-only cleanup.

## Consequences

The docs/adr files stay as they are. The owner can remove the stale ADRs and add the real decisions to decision-log.md in a separate change, as the saved memory note on ADRs suggests.

## How to reverse

Not needed. Nothing was changed.
