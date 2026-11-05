---
ticket: 38
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-05
---

# 0027. UAT not run for #38

## Context

The UAT stage could not check the running app: No verify.config.json found. The given path .ship-mnemo/phase-1-chat-and-bookmark-pages/t38/verify.config.json does not exist (there is no t38 directory), and the worktree root uat-38 has none either. The UAT rules forbid inferring or writing a config.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 38 by hand.
