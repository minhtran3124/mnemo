# Hard cases

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1 to 6

This file lists the cases that break the easy path, with the expected behavior and a pass condition for each.

## Purpose

Check honest failure and faithful summaries on real trouble. Supports F-02, F-09, F-10, NF-04. Links are in [sample-links.md](../../reference/sample-links.md). Rules: [README.md](README.md).

## Cases

| id | Case | Expected behavior | Pass condition |
| --- | --- | --- | --- |
| H-01 | PDF book, 580 pages, 14.6 MB | Code checks size and pages first. Send first pages and table of contents. Card says "summary from the first pages only". Limits are unverified. See [pdf-and-screenshots.md](../pdf-and-screenshots.md). | Card has the first-pages notice; no summary built from the printer cover only. |
| H-02 | Slack message link | App cannot open it. Card says "I cannot open Slack links. I saved the link only." and the paste hint Pasted text goes through the paste path. | Link saved or offered as paste; no summary; pasted text finds links. |
| H-03 | X post link (`https://x.com/addyosmani/article/2117512471930167377`) | Tool cannot read it. "Page not read" card; paste option. | `page_status` = `unreadable`, `summary` = `null`. |
| H-04 | bleepingcomputer.com article (fetch error) | Retry once if the error is transient (timeout, 5xx), then honest failure. A 4xx is not retried. Also a near-duplicate of the thehackernews.com Brotli article. | The `fetch` log shows one retry if the first outcome was `timeout` or `error` (5xx), and no retry for a 4xx; null summary either way; near-duplicate warning if comparison is possible. Record the real status code in the run log, because the cause is still unknown. |
| H-05 | YouTube video | Only the description is read. Card says the summary uses the description only. | Summary has no fact beyond the description; card says so. |
| H-06 | Repeat link with `fbclid` | URL is cleaned. Exact duplicate warning. | Warning text is "You saved this already". |
| H-07 | wearedevelopers.com/videos (list of many videos) | Does not fit one type. Proposed type `other`. Summary stays general. | Type is `other` if D-013 is built, otherwise the card is flagged. Open question. |
| H-08 | Vietnamese tutorial page | English summary (D-011). No language badge in version 1. | Summary in English with no unsupported facts. Not scored. |
| H-09 | arXiv HTML paper with raw math | Type `article`, tag `paper`. Summary does not copy raw math markup. | No raw markup in summary; tag `paper` present. |
| H-10 | Uber engineering blog (code in images) | Summary may miss image-only facts. | No invented facts from the missing images. |
| H-11 | Screenshot of the @0xShoopy X post | Type `image`. Visible text only. No URL needed. Ignore clutter. Do not state "Anthropic published this". | Card says "based on the visible text only"; no unsupported Anthropic claim; URL empty is accepted. |

## How to run

- Run each case once with the current prompt and save the card.
- A person reads each card against the pass condition. Code checks the null summary, notice texts and cleaned URL.
- Record results in the run log ([README.md](README.md)).
- At least 2 hard cases are in the held-out set.

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | Every unreadable case has a null summary. |
| 2 | H-11 never repeats the unsupported claim. |
| 3 | H-06 shows the exact-duplicate text. |

## Open questions

- Behavior of H-01 above the real API limits.
- Type for H-07.
