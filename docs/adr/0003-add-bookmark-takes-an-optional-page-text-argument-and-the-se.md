---
ticket: 27
stage: implement
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: implement)
date: 2026-11-05
---

# 0003. add_bookmark takes an optional page_text argument and the server sets id, saved_at and page_file

## Context

storage.md says add_bookmark(record) writes the page file but the record has no page text field.

## Options

- Put page text inside the record
- Separate page_text argument

## Decision

Signature add_bookmark(record, page_text=None); caller may not set id, saved_at or page_file.

## Why

Keeps the stored record equal to data-model.md fields exactly.

## Consequences

Later save-pipeline tickets call add_bookmark with page_text.

## How to reverse

Change the signature in store.py and storage.md.
