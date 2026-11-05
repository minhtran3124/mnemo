---
ticket: 32
stage: merge
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: merge)
date: 2026-11-05
---

# 0012. Merge PR 54 by hand for #32: gate review failed

## Context

The merge gate for #32 did not pass. review: 1 not fixed, 3 left at score 50 or more.

## Options

- n/a

## Decision

The workflow does not merge this PR into feat/phase-1-chat-and-bookmark-pages. After you have checked the failed gate, run: gh pr merge 54 --repo minhtran3124/mnemo --merge

## Why

Only a ticket PR that passes CI, review, intent review and has no open needs_review decision is merged by the workflow.

## Consequences

Ticket #32 is missing from the final PR and the tickets that depend on it are skipped until the PR is merged.

## How to reverse

Do not run the command; close the PR instead.
