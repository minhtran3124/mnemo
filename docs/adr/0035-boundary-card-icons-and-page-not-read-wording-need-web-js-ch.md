---
ticket: 42
stage: implement
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: implement)
date: 2026-11-05
---

# 0035. Boundary: card icons and Page-not-read wording need web/js/chat.js

## Context

The board chat card has a folder icon, a type icon and the X post paragraph. The card is built in web/js/chat.js, which the ticket does not name.

## Options

- Change chat.js
- Accept and record as A5

## Decision

Left chat.js alone and recorded the gap as A5 in ui-reference.md.

## Why

chat.js is outside the ticket's file list.

## Consequences

The chat card lacks the two icons and shows generic Page-not-read text until a ticket covers chat.js.

## How to reverse

Add the icons and wording in chat.js, then remove A5.
