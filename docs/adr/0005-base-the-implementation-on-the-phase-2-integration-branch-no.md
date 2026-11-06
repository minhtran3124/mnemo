---
ticket: 86
stage: research
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: research)
date: 2026-11-06
---

# 0005. Base the implementation on the phase-2 integration branch, not main

## Context

#80 to #85 are merged on github/feat/phase-2-eval-harness (6 commits ahead of main). github/main has no evals/ directory. CLAUDE.md says to open PRs to main.

## Options

- Base the implementation on github/feat/phase-2-eval-harness
- Base on github/main and wait for the integration branch to merge

## Decision

Base the implementation branch on github/feat/phase-2-eval-harness.

## Why

The ticket says all its dependencies are merged into the integration branch, and main lacks them, so the code cannot import save.preview, graders or faithful from main.

## Consequences

The PR for #86 targets the integration branch, not main. The reviewer must confirm the base branch before merge.

## How to reverse

Rebase onto main once the integration branch is merged to main.
