---
ticket: 37
stage: intent
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: intent)
date: 2026-11-05
---

# 0025. History response shape

## Context

The ticket says history returns messages with bookmark_ids plus a live-built cards list, without saying where the cards go. The Chat page ticket will read this.

## Options

- Top-level {messages, cards}
- Per-message cards list inside each message

## Decision

Return {messages:[...]} where each message has its own cards list, with {id, deleted: true} for a deleted bookmark.

## Why

The page draws each reply with its own cards, so no id lookup on the client is needed.

## Consequences

The Chat page ticket reads message.cards; changing it later means changing that client code.

## How to reverse

Move cards to a top-level map in the history handler and update the tests.
