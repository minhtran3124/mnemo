---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0031. Boundary: docs/adr files are outside the ticket file set

## Context

Finding F5 asks to delete the 11 autopilot-generated files in docs/adr/ (0001 to 0011), per the user's memory rule to keep D-rows in decision-log.md and drop these files. The boundary lists only server.py, intent.py, the listed tests, two feature-spec docs and the web bookmark files.

## Options

- Delete docs/adr/*.md anyway
- Skip and flag as a boundary issue

## Decision

Skip; change nothing.

## Why

The boundary rule says a fix touching a file outside the named set must change nothing and be returned as skipped. docs/adr/* is not named by any of the three tickets.

## Consequences

The 11 ADR files stay in the PR until someone removes them in a step whose boundary allows it. The finding remains valid.

## How to reverse

Run git rm -r docs/adr in a stage allowed to touch it, and add any needed D-rows to docs/process/decision-log.md.
