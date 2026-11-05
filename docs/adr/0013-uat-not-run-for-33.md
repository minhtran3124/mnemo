---
ticket: 33
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-05
---

# 0013. UAT not run for #33

## Context

The UAT stage could not check the running app: verify.config.json is missing at both allowed paths. The t33 folder under .ship-mnemo/phase-1-chat-and-bookmark-pages/ does not exist, and uat-33 (the worktree of github/feat/phase-1-chat-and-bookmark-pages at 1327df1) has no verify.config.json at its root. The UAT skill forbids inferring or writing a config, so the app was not started.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 33 by hand.
