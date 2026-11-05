---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0052. Boundary: skip F10 (Co-Authored-By trailers and docs/adr files)

## Context

CLAUDE.local.md forbids Claude attribution trailers and the user's memory says to drop autopilot-generated docs/adr files. About 88 commits in the range already carry the trailer, and docs/adr/*.md exists in the branch.

## Options

- Rewrite history to strip trailers and force-push
- Delete docs/adr/*.md in a new commit
- Change nothing and flag it for the owner

## Decision

Change nothing and flag it for the owner.

## Why

Stripping trailers needs a history rewrite and force-push, which the hard rules forbid. docs/adr/*.md is not in the file set of tickets #41, #42 or #43, so deleting it is out of bounds. The harness requires the trailer on new commits, which conflicts with the project-local rule, and that conflict cannot be settled here. A test that fails without the fix is not possible for a commit-message or history problem.

## Consequences

The branch keeps the trailers and ADR files until the owner removes them, for example by squash-merging with a clean message and dropping docs/adr in the PR.

## How to reverse

Not applicable, since nothing was changed.
