---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0019. Boundary: F3 NAT64 SSRF fix needs fetcher/guard.py, which no ticket in this run names

## Context

Finding F3 says is_allowed_address in fetcher/guard.py:28 accepts the NAT64 prefix 64:ff9b::/96 when it embeds a private or loopback IPv4 address, which bypasses the SSRF guard. The function only unwraps IPv4-mapped IPv6, and Python's is_global returns true for 64:ff9b::/96.

## Options

- Edit fetcher/guard.py and add a test under tests/ anyway
- Skip and flag the boundary so a ticket that owns fetcher/guard.py picks it up

## Decision

Skipped. Changed nothing and pushed nothing.

## Why

The file set for tickets #32 (save.py, prompts/save_system.txt, tests/test_save.py, docs/solutions/honest-failure.md), #33 (server.py, tests/test_bookmarks_api.py, docs/feature-specs/server-api.md) and #34 (web assets, server.py, theme and settings files, tests/test_web_assets.py, two docs) does not include fetcher/guard.py or tests/test_fetcher.py. The rules say a fix outside the set must be skipped.

## Consequences

The SSRF bypass stays open on this branch until a ticket that owns fetcher/guard.py and tests/test_fetcher.py covers it. The likely fix is to unwrap addresses in 64:ff9b::/96 (and 64:ff9b:1::/48) to their embedded IPv4 before the is_global check, or to refuse the prefix outright.

## How to reverse

Add fetcher/guard.py and tests/test_fetcher.py to a ticket's file set, then rerun this fix.
