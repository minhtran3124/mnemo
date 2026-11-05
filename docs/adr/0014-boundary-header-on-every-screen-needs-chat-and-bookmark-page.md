---
ticket: 34
stage: fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: intent-fix)
date: 2026-11-05
---

# 0014. Boundary: header on every screen needs chat and bookmark pages

## Context

Intent review says the theme control header is only on /settings. No other page exists in web/ or server.py yet; the chat and bookmark pages are separate tickets.

## Options

- Skip: the shared header partial plus render_page already exist, and later page tickets insert it
- Add placeholder chat and bookmark pages here to carry the header

## Decision

Skip. The shared partial and render_page are in place for later page tickets to reuse.

## Why

The ticket's out-of-scope lines exclude Chat page and Bookmark page content, and the file set does not name those pages. Adding them would break the boundary.

## Consequences

Only /settings shows the header until the chat and bookmark tickets use render_page.

## How to reverse

Have the chat and bookmark tickets call render_page with the <!--HEADER--> placeholder.
