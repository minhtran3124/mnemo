---
ticket: 30
stage: intent
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: intent)
date: 2026-11-05
---

# 0008. Accept DNS rebinding gap for phase 1

## Context

page-reading.md says pinning the connection to the checked address was not verified for httpx2 and asks to log the decision when built.

## Options

- pin connection to checked IP
- accept gap for a local single-user app

## Decision

Accept the gap, resolve and check before connecting, and note it in the docs.

## Why

Local, single-user, bound to 127.0.0.1; spec allows it for phase 1.

## Consequences

A hostile DNS server could rebind between check and connect; the open question stays in the docs.

## How to reverse

Add address pinning in fetcher/guard.py and page.py later.
