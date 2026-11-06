---
ticket: 86
stage: implement
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: implement)
date: 2026-11-06
---

# 0004. Boundary: branch based on the integration branch, not github/main

## Context

The task text said to create the worktree from github/main. github/main has no evals/ and none of #80 to #85, which this ticket depends on.

## Options

- Base on github/main
- Base on github/feat/phase-2-eval-harness (c208b19)

## Decision

Created the worktree from github/feat/phase-2-eval-harness, as the design says.

## Why

The ticket's dependencies exist only on the integration branch.

## Consequences

The PR for this ticket must target the integration branch.

## How to reverse

Rebase the three commits onto another base.
