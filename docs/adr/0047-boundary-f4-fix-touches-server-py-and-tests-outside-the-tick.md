---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0047. Boundary: F4 fix touches server.py and tests outside the ticket file set

## Context

Finding F4 says chat() in server.py (about line 342) calls intent.parse_note before intent.find_links. A message like 'note <id> ... <link>' is treated as a note and no link is saved. The project rule is that plain code (a URL regex) decides link versus question.

## Options

- Edit server.py (and add a test) to check find_links first
- Skip and report the boundary conflict

## Decision

Skip. Tickets #41, #42 and #43 name only docs, web/css, web/*.html and web/partials files. server.py and any pytest file are not listed, so editing them breaks the boundary.

## Why

The run rules say a fix that touches a file outside the named set must change nothing and be reported as a boundary decision.

## Consequences

F4 stays unfixed on this branch until a ticket that names server.py and its test file takes it. The ordering also needs a product call: parse_note currently wins, and the regex-wins rule says a link in the message should be saved.

## How to reverse

Not applicable, since nothing was changed. Add server.py and its test file to a ticket's file set and rerun the fix stage.
