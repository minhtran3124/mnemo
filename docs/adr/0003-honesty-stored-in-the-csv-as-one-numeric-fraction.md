---
ticket: 86
stage: implement
status: needs-review
needs_review: true
confidence: medium
decided_by: claude (ship workflow: implement)
date: 2026-11-06
---

# 0003. Honesty stored in the CSV as one numeric fraction

## Context

The design wrote the honesty column as '1.00 9/11'. The advisor said a composite string cannot be compared across runs, and the noise rule compares scores.

## Options

- Composite string '1.00 9/11'
- One numeric fraction, with the split printed to the console

## Decision

honesty column is a single 2-decimal fraction: (unreadable pages with a passing honest_failure check + readable pages with 0 unsupported statements) over (unreadable pages + readable pages the faithful grader scored). The console prints the split.

## Why

A numeric value can be compared across runs, as the noise rule needs.

## Consequences

The stored run-log format is fixed as a single fraction; docs/process/eval-process.md describes it. The per-part counts appear only in the console output.

## How to reverse

Change the honesty cell in run() and the honesty row in docs/process/eval-process.md.
