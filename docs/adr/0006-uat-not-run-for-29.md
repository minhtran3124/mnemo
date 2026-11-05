---
ticket: 29
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-05
---

# 0006. UAT not run for #29

## Context

The UAT stage could not check the running app: No verify.config.json found. It is missing at .ship-mnemo/phase-1-chat-and-bookmark-pages/t29/verify.config.json (the t29 directory does not exist) and at the root of the uat-29 worktree. The UAT rules say to write no config. The ticket also changes only client.py, a Python library with no UI or startable app, so there is nothing to drive in a browser.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 29 by hand.
