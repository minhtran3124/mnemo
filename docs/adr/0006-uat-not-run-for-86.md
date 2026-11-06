---
ticket: 86
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-06
---

# 0006. UAT not run for #86

## Context

The UAT stage could not check the running app: No verify.config.json exists at t86/verify.config.json or at the root of the uat-86 worktree. The UAT rules say not to infer, write or commit a config, so I did not start the app. The ticket also adds a CLI script, not a web app.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 86 by hand.
