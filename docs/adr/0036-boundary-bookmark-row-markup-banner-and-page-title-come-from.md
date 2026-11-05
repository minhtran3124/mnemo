---
ticket: 42
stage: implement
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: implement)
date: 2026-11-05
---

# 0036. Boundary: bookmark row markup, banner and page title come from server.py

## Context

The board shows a type icon, 'Article on host' wording, a count sentence, a search box, 'Show all N' and a 'Paste its text' button. The row and banner HTML is built in server.py.

## Options

- Change server.py
- Accept and record as A6 and A8

## Decision

Left server.py alone and recorded the gaps as A6 and A8.

## Why

server.py is outside the ticket's file list. Search is a later phase.

## Consequences

The bookmark page keeps its plain meta line and shorter banner.

## How to reverse

Change the markup in server.py, then remove A6 and A8.
