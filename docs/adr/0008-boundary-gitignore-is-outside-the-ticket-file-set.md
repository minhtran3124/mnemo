---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-04
---

# 0008. Boundary: .gitignore is outside the ticket file set

## Context

Finding F4 says the unanchored 'data/' in .gitignore:8 ignores any data directory at any depth, such as tests/data fixtures. The fix is to anchor it as '/data/'. The files named by tickets #10 and #13 are config.py, tests/test_config.py, pyproject.toml, .env.example, docs/reference/api-notes.md, docs/product/tech-stack.md, .githooks/pre-commit, tests/test_pre_commit.py, README.md, CLAUDE.md and docs/process/git-and-secrets.md. .gitignore is not among them.

## Options

- Edit .gitignore anyway
- Skip and report a boundary conflict

## Decision

Skip and report a boundary conflict. No file was edited.

## Why

The run rules say a fix that touches a file outside the named set must change nothing and return skipped.

## Consequences

The unanchored 'data/' rule stays in .gitignore until a ticket names the file. Until then a tests/data fixture directory would be silently ignored.

## How to reverse

Add .gitignore to a ticket's file list and re-run the fix, changing line 8 to '/data/' with a test that checks tests/data is not ignored.
