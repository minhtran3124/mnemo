---
ticket: 26
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-05
---

# 0002. UAT not run for #26

## Context

The UAT stage could not check the running app: No verify.config.json found. It is missing at .ship-mnemo/phase-1-chat-and-bookmark-pages/t26/verify.config.json (that t26 directory does not exist) and at the root of the uat-26 worktree. The UAT skill says never to infer or write a config, so the run did not happen.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 26 by hand.
