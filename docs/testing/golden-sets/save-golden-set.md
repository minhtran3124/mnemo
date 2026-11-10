# Save golden set

Status: Draft v0.1 · Owner: KhoiTran · Phase: 2

This file defines the 20-page Save set and the checks run on each saved bookmark.

## Purpose

Measure save quality, honesty and type accuracy. Supports F-20. Rules for all sets: [README.md](README.md).

## Set format

20 pages: a mix of GitHub READMEs, articles, tool pages and one unreadable page. All hard cases are included (the PDF, the Slack link, the YouTube video, the failed fetch, the repeat link, the index page). Of the 5 held-out pages, at least 2 are hard cases. Links: [sample-links.md](../../reference/sample-links.md).

The owner fills the blank columns. Do not invent them.

| id | source | expected type | expected tags (3 to 6) | key facts (2 to 4) | notes |
| --- | --- | --- | --- | --- | --- |
| S-01 | see sample-links.md |  |  |  |  |
| S-02 | see sample-links.md |  |  |  |  |
| S-03 | see sample-links.md |  |  |  |  |
| S-04 | see sample-links.md |  |  |  |  |
| S-05 | see sample-links.md |  |  |  |  |
| S-06 | see sample-links.md |  |  |  |  |
| S-07 | see sample-links.md |  |  |  |  |
| S-08 | see sample-links.md |  |  |  |  |
| S-09 | see sample-links.md |  |  |  |  |
| S-10 | see sample-links.md |  |  |  |  |
| S-11 | see sample-links.md |  |  |  |  |
| S-12 | see sample-links.md |  |  |  |  |
| S-13 | see sample-links.md |  |  |  |  |
| S-14 | see sample-links.md |  |  |  |  |
| S-15 | see sample-links.md |  |  |  |  |
| S-16 | see sample-links.md |  |  |  |  |
| S-17 | see sample-links.md |  |  |  |  |
| S-18 | see sample-links.md |  |  |  |  |
| S-19 | see sample-links.md |  |  |  |  |
| S-20 | see sample-links.md |  |  |  |  |

Mark the 5 held-out rows with `held-out` in notes. Never use them as prompt examples.

## Checks on a saved bookmark

| Check | Type | What it tests |
| --- | --- | --- |
| Valid JSON and schema | Code | All fields present, only allowed values (see [data-model.md](../../feature-specs/data-model.md)). |
| Tag rules | Code | 3 to 6 lowercase tags. |
| Summary length | Code | At most 60 words. |
| Honest failure | Code | An unreadable page gives a null summary. The most important check. |
| Type match | Code | The type equals your expected type. |
| Tag overlap | Code | Share of your expected tags found in the app's tags. |
| Faithful summary | Model | The grader reads the page text and the summary and lists every statement the page does not support. The count must be 0. It also says yes or no for each key fact. |

## Run rules

- Run the baseline twice; the gap is the noise level.
- Change one thing per run (prompt version, model).
- Read 3 results and the grader's reasons after each run.
- One CSV row per run: run id, prompt version, model, the three scores, tokens used.

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | One command scores all 20 pages and prints three numbers: save quality, honesty, find rate (find rate appears once the Ask set exists). |
| 2 | Honest failure score is 100 percent. |
| 3 | Faithful-summary count is 0 for each page. |

## Open questions

- Which 5 are held-out.
- Pass targets for type match and tag overlap (after first baseline).
