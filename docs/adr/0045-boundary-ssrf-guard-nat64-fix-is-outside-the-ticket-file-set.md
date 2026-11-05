---
ticket: run
stage: fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0045. Boundary: SSRF guard NAT64 fix is outside the ticket file set

## Context

Finding F3 says is_allowed_address in fetcher/guard.py only unwraps IPv4-mapped IPv6, so 64:ff9b::/96 addresses embedding loopback or private IPv4 pass as global. Tickets #41, #42 and #43 name only docs and web UI files, and none names fetcher/guard.py or a guard test file.

## Options

- Skip and flag the boundary
- Edit fetcher/guard.py and add a test anyway

## Decision

Skip. Changed nothing and pushed nothing.

## Why

The run rules say a fix touching a file outside the named set must change nothing and return skipped. The finding looks valid: in the file read, is_allowed_address only unwraps ipv4_mapped. It needs a ticket that covers fetcher/guard.py and its test.

## Consequences

The NAT64 SSRF gap stays open on the branch until a ticket that covers fetcher/guard.py is run.

## How to reverse

Add fetcher/guard.py and its guard test file to a ticket's file list, then rerun the fix stage.
