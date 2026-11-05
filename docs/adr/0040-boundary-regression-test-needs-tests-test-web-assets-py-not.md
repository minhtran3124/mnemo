---
ticket: 42
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0040. Boundary: regression test needs tests/test_web_assets.py, not named by ticket #42

## Context

Finding F1: the custom radio (.choice input:checked) and pressed theme and view buttons show state only by background or box-shadow, which forced-colors mode removes. The fix is an @media (forced-colors: active) block in web/css/base.css and web/css/bookmarks.css that uses Highlight, HighlightText and Canvas. The stage requires a test that fails without the fix.

## Options

- Add the CSS fix and the test in tests/test_web_assets.py, which is outside the file set
- Skip and report the boundary
- Ship the CSS fix with no test

## Decision

Skip and change nothing

## Why

The file set says a test file is in bounds only when listed, and tests/test_web_assets.py is not listed. A fix with no test breaks the stage requirement. I wrote the fix, the test passed with it, and ruff was clean, then I reverted it all.

## Consequences

F1 stays unfixed on this branch until the ticket's file set includes tests/test_web_assets.py, or the owner accepts a fix without a test.

## How to reverse

Add tests/test_web_assets.py to the ticket's file set and rerun the fix stage. The change is a forced-colors block in base.css and bookmarks.css plus one test.
