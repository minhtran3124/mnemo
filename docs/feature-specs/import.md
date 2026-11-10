# Import the old pile

Status: Draft v0.1 · Owner: KhoiTran · Phase: 4

This file describes how you bring links from browser bookmarks, notes and messages into one place.

## Purpose

Your links live in three places. Import puts them in one. Supports F-06 and job 9 of the plan.

## Scope

In: browser export file, pasted text, link finder, estimate, batches, unreadable links.
Out: a direct Slack connection (not planned for version 1; it needs app approval and extra work).

## Requirements

| ID | Requirement |
| --- | --- |
| IM-01 | An import page accepts the bookmarks file that your browser exports. |
| IM-02 | The page also accepts pasted text from Slack, a notes app or messages. |
| IM-03 | A link finder (plain code) finds the links in pasted text. |
| IM-04 | Before it starts, the page shows the number of links and a cost estimate. |
| IM-05 | Links are processed in batches of about 20. You can stop at any time. |
| IM-06 | Unreadable links are expected. Each one is saved as link only (F-02). |
| IM-07 | Phase 4 skips a link whose `url_clean` is already saved (exact match, code only, `store.find_by_url_clean`) and shows a count. The near-duplicate warning is phase 5 ([duplicates.md](duplicates.md)). |
| IM-08 | Imported bookmarks get `source` = `import` (proposed field). |

## Behavior and rules

1. You choose a file or paste text.
2. Code finds links and cleans them.
3. The page shows: "N links found" and an estimated cost. Cost formula: Open question. Unverified: current Claude API prices.
4. You press Start. The server processes about 20 links, then reports.
5. You press Continue or Stop. A stopped import keeps what is already saved.

- Pasting Slack text is fine because the Slack workspace is personal. A Slack message link cannot be read; paste the message text instead.
- Mind privacy: only public links while building (D-018). Imports can contain work links. See [privacy-and-security.md](privacy-and-security.md).

## Link finder

`mnemo/chat/importer.py` holds the plain-code link finder used before any Claude call (IM-03):

- `links_from_browser_export(html)` reads the Netscape bookmarks file a browser exports.
- `links_from_text(text)` finds links in pasted text with `intent.find_links`.

Both clean each link with `urlclean.clean_url`, drop duplicates on the cleaned link, keep first-seen order and reject non-web links (`about:`, `javascript:`, `file:`, or a link with no host). A non-string input raises `ValueError`; empty text or a file with no links returns an empty list.

Each result is a dict: `{"url": <link as written>, "url_clean": <cleaned link>, "slack": <bool>}`. `slack` is true when the link is a `*.slack.com/archives/...` message link, so the page can tell you it cannot be read.

## Edge cases

| Case | Behavior |
| --- | --- |
| Duplicate inside the file | Saved once. |
| Link already saved | Skipped with a count. |
| Dead or blocked link | Link only, "page not read". |
| Very large file | Batches keep the cost visible. Open question: maximum count. |
| Text with no link | "No links found." |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | A browser export and a pasted Slack text both give a link count. |
| 2 | A cost estimate is shown before any API call. |
| 3 | Pressing Stop after the first batch leaves exactly the saved items. |
| 4 | An unreadable link is saved as link only with a null summary. |
| 5 | Your own old pile imports in small batches (phase 4 done-check). |

## Tests

Use a small export file and one pasted text. Cases: [hard-cases.md](../testing/golden-sets/hard-cases.md).

## Open questions

- How many links are in your Slack now (plan question 3).
- Cost estimate formula.
- Browser export format details for your browser.
