---
ticket: 42
stage: implement
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: implement)
date: 2026-11-05
---

# 0037. Boundary: Settings bookmark view section and preview need a script change

## Context

The Settings board has a 'Bookmark view' radio group and a preview entry. The choice is stored by web/js/view-switcher.js, which the ticket does not name.

## Options

- Add an inline script in settings.html
- Change view-switcher.js
- Accept and record as A10

## Decision

Did not build the section and recorded it as A10.

## Why

It needs a script change outside the ticket's files, and ui-reference.md lists Compact as phase 3.

## Consequences

The Settings screens differ from the phone board in two sections.

## How to reverse

Add the radio group wired to view-switcher.js, then remove A10.
