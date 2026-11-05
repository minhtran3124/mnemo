---
ticket: 42
stage: fix
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0034. Boundary: keep guess badge in warn colour

## Context

Finding F2 says .badge (guess) in web/css/bookmarks.css uses warn colour and looks like the page-not-read badge. ui-reference.md line 75 specifies the bookmark row guess flag as a bordered warn flag, and chat.css .flag uses the same warn border and text. The not-read badge is .badge.badge-warn, which adds a filled warn-bg and warn-text.

## Options

- Leave as is (matches V3 spec and chat flag)
- Recolour the guess badge to a muted or ink border

## Decision

Leave as is and skip the fix.

## Why

Recolouring departs from the V3 boards and the spec and would be a new design decision, which ticket #42 lists as out of scope. The two badges are already told apart by fill and by text.

## Consequences

The guess badge and the page-not-read badge share a warn hue; they differ in fill and wording.

## How to reverse

Change the .badge border and colour in web/css/bookmarks.css to a muted token and update ui-reference.md line 75 and the chat .flag together.
