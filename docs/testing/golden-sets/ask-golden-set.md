# Ask golden set

Status: Draft v0.1 · Owner: KhoiTran · Phase: 4

This file defines the Ask set: 15 real questions and 3 trick questions.

## Purpose

Measure whether the right bookmark is in the top 3, and whether the app says "nothing found" when it should. Supports F-07, F-08, F-20. Rules: [README.md](README.md).

## Format

- 15 questions you wrote, each with the expected bookmark.
- 3 trick questions with no answer in your list. The right result is "nothing found".

| id | question | kind | expected bookmark | notes |
| --- | --- | --- | --- | --- |

The owner writes the questions in her own words. Rows below are examples only, to show the format. Do not use them as real questions.

| id | question | kind | expected bookmark | notes |
| --- | --- | --- | --- | --- |
| A-01 | (example) "what was that tool for forms?" | real | S-xx (owner fills) | Example only |
| A-02 | (example) "what did I save about caching?" | real | S-xx (owner fills) | Example only |
| A-03 | (example) "anything about Brotli?" | real | S-xx (owner fills) | Example only. Two near-duplicate articles may both match |
| T-01 | (example) a topic not in the list | trick | none | Example only. Expected: "nothing found" |
| T-02 | (example) a topic not in the list | trick | none | Example only |

Blank rows for the owner:

| id | question | kind | expected bookmark | notes |
| --- | --- | --- | --- | --- |
| A-04 to A-15 |  | real |  |  |
| T-03 |  | trick | none |  |

## Checks on an answer

| Check | Type | What it tests |
| --- | --- | --- |
| Numbers exist | Code | Every bookmark number in the answer exists. |
| Trick question | Code | A trick question returns no bookmark. |
| Top 3 | Code | How often the right bookmark is in the top 3 (retrieval check). |
| Supported answer | Model | Yes or no: is the answer supported by the bookmarks it cites? |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | All 18 run without a missing tool result. |
| 2 | All 3 trick questions return "nothing found". |
| 3 | Find rate is written down as a baseline. A target is set after it. |

## Open questions

- The 15 questions (owner writes).
- Whether questions in Vietnamese are tested (not in version 1).
