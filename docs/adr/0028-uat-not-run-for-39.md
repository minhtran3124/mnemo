---
ticket: 39
stage: uat
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: uat)
date: 2026-11-05
---

# 0028. UAT not run for #39

## Context

The UAT stage could not check the running app: Neither config file exists. /home/minhtran/Documents/minh.tran/projects/.ship-mnemo/phase-1-chat-and-bookmark-pages/t39/verify.config.json is missing (there is no t39 directory), and there is no verify.config.json at the root of the worktree /home/minhtran/Documents/minh.tran/projects/.ship-mnemo/phase-1-chat-and-bookmark-pages/uat-39. The UAT rules say not to infer, write or commit a config, so the app was not started and no scenarios were run.

## Options

- n/a

## Decision

Continue without UAT; the ticket stays done and the PR body says UAT did not run.

## Why

A missing config, a start failure or an agent failure is not an acceptance failure, so no code fix is attempted.

## Consequences

The running app was not checked against the original request.

## How to reverse

Run /harness:uat 39 by hand.
