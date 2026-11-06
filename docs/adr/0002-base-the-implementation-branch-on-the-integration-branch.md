---
ticket: 86
stage: design
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: design)
date: 2026-11-06
---

# 0002. Base the implementation branch on the integration branch

## Context

github/main has no evals/. The modules #86 depends on exist only on github/feat/phase-2-eval-harness (tip c208b19), and the ticket says they are merged into the integration branch.

## Options

- Branch from github/feat/phase-2-eval-harness and target it
- Branch from main

## Decision

Branch from github/feat/phase-2-eval-harness and open the PR against it.

## Why

The code cannot import its dependencies from main.

## Consequences

The PR targets the integration branch, not main. The worktree created from main must be recreated or reset to the integration tip in the implement stage.

## How to reverse

Rebase onto main once the integration branch is merged.
