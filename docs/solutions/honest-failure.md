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
5. Offer a Paste text field. If you paste text, run the normal save on that text. For an existing link-only bookmark, `POST /api/bookmarks/:id/paste` fills in that same bookmark (no second copy): the text is cut once, sent to Claude and stored as `data/pages/<id>.txt`, and `page_status` becomes `ok`. Text under 40 characters gives 400 `text_too_short`; invalid output twice gives 502 `summary_failed` and the bookmark stays link only with no page file. A user-written reason is kept.
6. For a partial read (for example only a video description), the card says what was used.
7. Show a "page not read" badge on the bookmark page row.

"Too short" means under 300 characters for HTML and under 40 for GitHub, after whitespace is collapsed. Set in `config.py` (`MIN_TEXT_CHARS_HTML`, `MIN_TEXT_CHARS_GITHUB`). Pasted text skips the fetch but has its own floor of 40 characters (`MIN_TEXT_CHARS_PASTED`), so a one-character paste is saved as link only with `page_status` `unreadable` and a null summary. The text Claude sees is the text stored in `data/pages/<id>.txt`: whitespace collapsed once, cut to `MAX_PAGE_CHARS` once.

## Claude API errors on save

The rule: a revoked or wrong key must never look like an unreadable page.

| Case | Behavior |
| --- | --- |
| Transient: connection error, timeout, 429, 5xx, 408, 409, 529 | Retry once. If it fails again, save link only. |
| Invalid output: refusal, `max_tokens`, schema mismatch, failed code checks (tags, words, type, title) | Retry once. If it fails again, save link only. No further identical retries. |
| Permanent: 400, 401, 403, 404, any other 4xx, or a missing `ANTHROPIC_API_KEY` | Not retried and not swallowed. The error propagates and nothing is saved. |

Each retry and each link-only fallback is logged once with the exception class and status code. No key and no page text is logged, and nothing is logged on success.

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
