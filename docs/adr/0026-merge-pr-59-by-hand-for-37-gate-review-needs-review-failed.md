---
ticket: 37
stage: merge
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: merge)
date: 2026-11-05
---

# 0026. Merge PR 59 by hand for #37: gate review, needs_review failed

## Context

The merge gate for #37 did not pass. review: 1 not fixed, 0 left at score 50 or more. needs_review: 1 (History response shape).

## Options

- n/a

## Decision

The workflow does not merge this PR into feat/phase-1-chat-and-bookmark-pages. After you have checked the failed gates, run: gh pr merge 59 --repo minhtran3124/mnemo --merge

## Why

Only a ticket PR that passes CI, review, intent review and has no open needs_review decision is merged by the workflow.

## Consequences

Ticket #37 is missing from the final PR and the tickets that depend on it are skipped until the PR is merged.

## How to reverse

Do not run the command; close the PR instead.
