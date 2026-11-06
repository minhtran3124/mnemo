---
ticket: 99
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-06
---

# 0001. UAT not run for #99

## Context

The UAT stage could not check the running app: verify.config.json is missing at both allowed paths. The given path .ship-mnemo/phase-2-follow-ups/t99/verify.config.json does not exist (the t99 directory is there, but it holds no config and not even a worktree). The fallback at the root of the uat-99 worktree does not exist either. The skill does not allow inferring or writing a config. The uat-99 worktree itself was created at f28f48d.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 99 by hand.
