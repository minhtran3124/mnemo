---
ticket: 10
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-04
---

# 0005. Boundary: phase-0-setup.md plan is outside ticket #10's file set

## Context

Finding F5 says Task 3 in docs/product/plans/phase-0-setup.md still lists the model-name check as open (Unverified), and the plan does not mention config.py, .env.example or the tests. The ticket's file list names config.py, tests/test_config.py, pyproject.toml, .env.example, docs/reference/api-notes.md and docs/product/tech-stack.md, but not the plan file.

## Options

- Edit the plan file anyway
- Skip and flag the boundary

## Decision

Skip. No file was changed, committed or pushed.

## Why

The only place the finding can be fixed is the plan file, which is a doc file outside the ticket's file set. The rule says to change nothing in that case.

## Consequences

Task 3 in the plan keeps its stale Unverified wording until a ticket that names the plan file covers it.

## How to reverse

Add docs/product/plans/phase-0-setup.md to the ticket's file list, or open a follow-up ticket that names it, then rerun this fix.
