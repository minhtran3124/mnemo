---
ticket: run
stage: review-fix
status: needs-review
needs_review: true
confidence: high
decided_by: claude (ship workflow: review-fix)
date: 2026-11-05
---

# 0030. Boundary: F3 fix needs fetcher/page.py and fetcher/github.py

## Context

Finding F3 says with_retry in fetcher/page.py catches only httpx2.HTTPError at line 93, so a malformed redirect Location (InvalidURL) escapes fetch(). github._attempt in fetcher/github.py has the same hole. The run's tickets (#37, #38, #39) name only server.py, intent.py, web/ files, two test files and two docs; no fetcher/ file and no test file for the fetcher.

## Options

- Edit fetcher/page.py and fetcher/github.py anyway
- Skip and report a boundary conflict

## Decision

Skip and change nothing.

## Why

The rules say a fix touching a file outside the ticket file set must change nothing and return skipped.

## Consequences

F3 stays open on this branch. A ticket that owns fetcher/page.py and fetcher/github.py needs to take it. The change is to catch InvalidURL and other non-HTTPError httpx errors in with_retry and github._attempt and return FetchFail, plus a test that uses a redirect to a malformed Location.

## How to reverse

Add fetcher/page.py, fetcher/github.py and a fetcher test file to a ticket's file list, then rerun the fix stage.
