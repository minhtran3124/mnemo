# Solution: Honest Failure
Status: Draft v0.1 · Owner: KhoiTran · Phase: 1

How Mnemo behaves when it cannot read a page (feature F-02).

## Problem
Many pages cannot be read: logins, paywalls, pages built with JavaScript, blocked tools. If the app writes a summary anyway, it invents facts. One wrong summary breaks trust.

## Context
- The X post sample could not be read by the fetch tool.
- bleepingcomputer.com gave a fetch error, and the reason is unknown.
- The Slack link needs a sign-in.
- The YouTube sample gave only the description, not the video.
- The plan says fetch errors are normal.

## Solution
1. The server fetches the page. If it fails, it retries once.
2. If the fetch still fails, or the text is too short, save the link only.
3. Set `page_status` to `unreadable` and `summary` to null.
4. Show a "Page not read" card: "I could not read this page. I saved the link only."
5. Offer a Paste text field. If you paste text, run the normal save on that text.
6. For a partial read (for example only a video description), the card says what was used.
7. Show a "page not read" badge on the bookmark page row.

Open question: what "too short" means in characters. The plan does not set a number.

## Why
- Product rule 2: be right, or say you are not sure.
- NF-04: never write a summary of text the app did not see.
- Tested by the most important code check: an unreadable page gives a null summary.

## Where used
F-01, F-02, F-04. See [page reading](../feature-specs/page-reading.md) and [phase 1 plan](../product/plans/phase-1-chat-and-bookmark-pages.md).

## Tests
| Test | Expected |
| --- | --- |
| Save the X post link | `page_status` unreadable, `summary` null, card says it |
| Save a link where the fetch fails with a transient error (timeout, 5xx) | One retry, then link-only card |
| Paste text on a failed card | Summary uses only the pasted text |
| Eval code check | Unreadable page gives a null summary on every run |
| Screenshot with cut text | Card says "based on the visible text only" |
