---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0048. Boundary: F8 targets a file absent from the branch

## Context

Finding F8 points at web/partials/header.html:4, but the fetched branch tip 2453d01 tracks no web/ directory (only Python modules, tests and docs). The finding was probably raised against a different tree, such as the owner's checkout, which has uncommitted or unpushed UI work.

## Options

- Skip and report
- Create web/partials/header.html and the Bookmarks page from scratch

## Decision

Skip and report; change nothing.

## Why

Creating the header partial and the UI would be a large change beyond one link, and a test that fails without the fix cannot be written against files that do not exist.

## Consequences

F8 stays open until the UI files are on the branch. Re-run the fix after they are pushed.

## How to reverse

Push the web/ files to the branch and re-run the fix stage for F8.
