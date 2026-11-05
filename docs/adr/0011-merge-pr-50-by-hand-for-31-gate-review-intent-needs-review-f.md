---
ticket: 31
stage: merge
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: merge)
date: 2026-11-05
---

# 0011. Merge PR 50 by hand for #31: gate review, intent, needs_review failed

## Context

The merge gate for #31 did not pass. review: the intent fix commits were not reviewed. intent: gaps found. needs_review: 1 (Boundary: keep extra server tests; 4 passed is not literally achievable).

## Options

- n/a

## Decision

The workflow does not merge this PR into feat/phase-1-chat-and-bookmark-pages. After you have checked the failed gates, run: gh pr merge 50 --repo minhtran3124/mnemo --merge

## Why

Only a ticket PR that passes CI, review, intent review and has no open needs_review decision is merged by the workflow.

## Consequences

Ticket #31 is missing from the final PR and the tickets that depend on it are skipped until the PR is merged.

## How to reverse

Do not run the command; close the PR instead.
