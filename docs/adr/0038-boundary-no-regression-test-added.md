---
ticket: 42
stage: intent-fix
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: intent-fix)
date: 2026-11-05
---

# 0038. Boundary: no regression test added

## Context

The task asks for a test that fails without the fix, but the ticket file set does not list any test file.

## Options

- Add a test in tests/test_view_switcher.py
- Skip the test and keep the fix inside the listed files

## Decision

Kept the fix to the listed CSS and doc files and added no test. A draft test for the new row-title token passed locally and was reverted.

## Why

The boundary says a test file is in bounds only when listed.

## Consequences

The phone text-size fix has no automated guard; it was checked with computed styles in a browser.

## How to reverse

Add a test asserting --row-title-size in base.css and its use in bookmarks.css.
