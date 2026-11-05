---
ticket: 31
stage: intent-fix
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: intent-fix)
date: 2026-11-05
---

# 0010. Boundary: keep extra server tests; 4 passed is not literally achievable

## Context

The owner-confirmed Verify says `uv run pytest tests/test_server.py -q` prints `4 passed`. tests/test_server.py defines 4 required tests plus about 14 more (API-key leak, 405 and Allow header, 500 handling, a docs-spec check, parametrized status cases). The run reports roughly 30 passed.

## Options

- Delete the extra tests so exactly 4 remain
- Move the extra tests into a new test file (e.g. tests/test_server_errors.py)
- Leave the tests and treat '4 passed' as the minimum required tests, not an exact count

## Decision

Change nothing and skip. Deleting tests would weaken coverage, which the rules forbid. A new test file is not in the ticket's named file set.

## Why

The hard rule against weakening tests and the ticket's file-set limit both block the only ways to make the output read exactly `4 passed`. The literal count most likely meant at least the 4 required tests.

## Consequences

The Verify line stays unmet if read as an exact count. All 4 required tests exist and pass, along with the extras.

## How to reverse

The owner can either allow a new tests/test_server_errors.py (move the extras there) or reword the Verify line to 'exits 0'.
