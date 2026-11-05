---
ticket: 30
stage: implement
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: implement)
date: 2026-11-05
---

# 0007. Boundary: README not updated for GITHUB_TOKEN

## Context

technical.md says to list each new env variable in README.md, but README.md is not in the ticket's file list.

## Options

- Edit README.md
- Leave it and report

## Decision

Left README.md unchanged; GITHUB_TOKEN (optional) still needs a README line.

## Why

A change outside the named files is not made.

## Consequences

The optional GITHUB_TOKEN variable is undocumented in README until a follow-up.

## How to reverse

Add a GITHUB_TOKEN line to README.md.
