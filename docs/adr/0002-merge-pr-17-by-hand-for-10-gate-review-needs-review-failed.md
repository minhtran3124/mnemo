---
ticket: 10
stage: merge
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: merge)
date: 2026-11-04
---

# 0002. Merge PR 17 by hand for #10: gate review, needs_review failed

## Context

The merge gate for #10 did not pass. review: 3 not fixed, 2 left at score 50 or more. needs_review: 4 (Boundary: other docs still call the model name unchecked; Boundary: ci.yml pytest exit-5 tolerance is outside ticket #10 files; Boundary: docs/README.md is not in ticket #10 file set; Boundary: phase-0-setup.md plan is outside ticket #10's file set).

## Options

- n/a

## Decision

The workflow does not merge this PR into feat/phase-0-setup. After you have checked the failed gates, run: gh pr merge 17 --repo minhtran3124/mnemo --merge

## Why

Only a ticket PR that passes CI, review, intent review and has no open needs_review decision is merged by the workflow.

## Consequences

Ticket #10 is missing from the final PR and the tickets that depend on it are skipped until the PR is merged.

## How to reverse

Do not run the command; close the PR instead.
