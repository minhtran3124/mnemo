---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0049. Boundary: docs/adr files are outside the allowed file set

## Context

Finding F9 asks to remove the autopilot-generated docs/adr files (11 files exist on the branch vs github/main, not 33). None of them appear in the files named by tickets #41, #42 or #43.

## Options

- Delete docs/adr files anyway
- Skip and flag for the owner or the ADR-writing stage

## Decision

Skip and flag; no files changed.

## Why

The task rules say a fix touching a file outside the named set must change nothing and return skipped with a Boundary decision.

## Consequences

The docs/adr files remain on the PR branch until the owner or a stage with wider scope removes them. The user's memory rule says to keep only D-rows in docs/process/decision-log.md.

## How to reverse

Not applicable, nothing changed.
