---
ticket: 13
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-04
---

# 0006. UAT not run for #13

## Context

The UAT stage could not check the running app: No verify.config.json found. It is missing at /home/minhtran/Documents/minh.tran/projects/.ship-mnemo/phase-0-setup/t13/verify.config.json (that directory does not exist) and at the root of the worktree /home/minhtran/Documents/minh.tran/projects/.ship-mnemo/phase-0-setup/uat-13. The UAT skill forbids inferring or writing a config, so no run was attempted. The worktree was created from github/feat/phase-0-setup and the recipe file exists.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 13 by hand.
