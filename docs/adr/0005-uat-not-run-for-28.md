---
ticket: 28
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-05
---

# 0005. UAT not run for #28

## Context

The UAT stage could not check the running app: verify.config.json is missing at both allowed paths. It is not in .../phase-1-chat-and-bookmark-pages/t28/ (that directory does not exist) and it is not at the root of the uat-28 worktree. The UAT rules say to infer, write or commit no config, so no scenarios ran. The ticket is also a pure function with no network call, so there may be no app to start.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 28 by hand.
