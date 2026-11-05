---
ticket: 42
stage: review-fix
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0041. Boundary: regression test for main width lives in a file outside ticket #42

## Context

F3 is real. base.css `main` has max-width 40rem and padding var(--page-pad) (3rem), so the content column is 34rem on laptop. Chat and bookmarks use calc(Nrem + 2 * var(--page-pad)). The fix is `max-width: calc(40rem + 2 * var(--page-pad));`. A test that fails without it would go in tests/test_web_assets.py (it has the rule_body helper for base.css), and that file is not in the ticket's list of files.

## Options

- Skip, change nothing
- Edit base.css and add the test to tests/test_web_assets.py anyway
- Edit base.css with no test

## Decision

Skip, change nothing

## Why

The file-set rule says a test or doc file is in bounds only when listed, and a fix that needs an unlisted file changes nothing. The task also requires a test that fails without the fix.

## Consequences

F3 stays open. Settings column stays 34rem wide at laptop width until the file set is widened to include tests/test_web_assets.py.

## How to reverse

Add tests/test_web_assets.py to the ticket's file list, then apply the one-line base.css change and a test asserting `main` max-width includes 2 * var(--page-pad).
