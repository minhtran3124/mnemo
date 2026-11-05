---
ticket: run
stage: fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0016. Boundary: README.md not in the file set for the GITHUB_TOKEN row

## Context

Finding F8: the optional GITHUB_TOKEN (read in config.py, used in fetcher/github.py) is missing from the README Environment variables table, against D-023 which says new variables are listed in README.md. README.md is not named by tickets #32, #33 or #34.

## Options

- Add the row to README.md anyway
- Skip and flag the boundary

## Decision

Skip and flag the boundary; no files changed.

## Why

The boundary rule says a fix touching a file outside the set must change nothing and return skipped.

## Consequences

GITHUB_TOKEN stays undocumented in README until a ticket that names README.md covers it.

## How to reverse

Add a `GITHUB_TOKEN` row (optional, raises the GitHub API limit from 60 to 5,000 requests per hour, read by config.py) to the README Environment variables table in a ticket that lists README.md.
