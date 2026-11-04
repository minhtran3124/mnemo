---
ticket: 10
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-04
---

# 0004. Boundary: docs/README.md is not in ticket #10 file set

## Context

Finding F4 says the Known gaps line at docs/README.md:61 claims model names are not checked, which this PR makes false. The ticket names only config.py, tests/test_config.py, pyproject.toml, .env.example, docs/reference/api-notes.md and docs/product/tech-stack.md.

## Options

- Edit docs/README.md anyway
- Skip and flag the boundary for the owner

## Decision

Skip. Make no change and push nothing.

## Why

A doc file is in bounds only when the ticket lists it, and docs/README.md is not listed. The project rule to fix docs in the same session cannot override the ticket boundary.

## Consequences

The Known gaps line in docs/README.md still says model names are not checked until the owner adds the file to the ticket or fixes it in a follow-up.

## How to reverse

Add docs/README.md to the ticket file set and re-run the fix stage, or edit the line in a follow-up change.
