# Page reading

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1

This file says how the server gets the text of a page, and what it does when that fails.

## Purpose

Claude can only summarize what it sees. The fetcher (a small program that downloads a page and takes out its text) gives Claude that text. Page fetching is not in the course, so expect failures. Supports F-01, F-02, NF-02, NF-04.

## Scope

In: fetcher, GitHub API, retry, text limits, honest failure, YouTube, link cleaning, language.
Out: PDFs and screenshots (see [pdf-and-screenshots.md](pdf-and-screenshots.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| PR-01 | The fetcher is code in `fetcher/`. Claude Code writes it. |
| PR-02 | For GitHub repos, use the official GitHub API: description and README. |
| PR-03 | If a fetch fails, retry once. Then show the honest failure card. |
| PR-04 | If the text is shorter than a minimum length, treat the page as unreadable. |
| PR-05 | Cut page text at a maximum page length (NF-02). Both limits live in `config.py`. |
| PR-06 | An unreadable page is saved as link only: `page_status` = `unreadable`, `summary` = `null`. |
| PR-07 | For YouTube, use only the video description. The card says so. |
| PR-08 | Clean tracking parts from the link before saving (see below). |

Minimum length and maximum length values: Open question. Set them in `config.py` and tune in phase 1.

## Behavior and rules

- Honest failure text: "I could not read this page. Saved the link only." Never a made-up summary.
- Known cases: X post (not readable by the plan's test tool), Slack link (needs sign-in), bleepingcomputer.com (fetch error, cause unknown), pages built with JavaScript, paywalls, logins.
- Cutting long text: the card should say when text was cut. Open question: wording.
- Saved text goes to `data/pages/<id>.txt`. The same text is used by the eval, so each run sees the same input.

### Link cleaning (short)

Remove tracking parts such as `fbclid` and `utm_*` before comparing or saving `url_clean`. Full rules: [duplicates.md](duplicates.md).

### Language rule

Version 1 writes English summaries only (D-011). A Vietnamese page gets an English summary. No language badge in version 1. The Vietnamese tutorial stays in the set as an extra case and is not scored.

## Edge cases

| Case | Behavior |
| --- | --- |
| Page is a marketing page | Summary stays general, no invented product details. |
| Math shown as raw markup (arXiv) | Summary must not copy the raw markup. |
| Code only in images (Uber blog) | Summary may miss those facts. Accepted. |
| Site name wrongly guessed by a tool | Faithful-summary grader catches it. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | A failed fetch is retried once (checked in logs). |
| 2 | Text below the minimum gives `unreadable` and a null summary. |
| 3 | Text above the maximum is cut before the API call. |
| 4 | A YouTube card says the summary uses the description only. |
| 5 | A link with `fbclid` is saved without it. |

## Tests

[hard-cases.md](test-cases/hard-cases.md), [save-golden-set.md](test-cases/save-golden-set.md). Links: [sample-links.md](../reference/sample-links.md).

## Open questions

- Minimum and maximum text length.
- Time limit for a fetch.
- Do the rules of a site (terms of use) limit saving its text? The plan says: keep text on your disk and do not share it.
