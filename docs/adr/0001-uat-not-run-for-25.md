---
ticket: 25
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-05
---

# 0001. UAT not run for #25

## Context

The UAT stage could not check the running app: verify.config.json was found neither at /home/minhtran/Documents/minh.tran/projects/.ship-mnemo/phase-1-chat-and-bookmark-pages/t25/verify.config.json nor at the root of the uat-25 worktree. The uat skill forbids inferring or writing a config. The worktree at that commit has no server or UI (client.py, config.py, urlclean.py only), so there is no app to start in a browser.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 25 by hand.
