# Definition of Done
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file says when a feature and a phase count as done. "Done" means a person has checked it, not only that code exists.

## Per feature
A feature is done when all rows are true.

| # | Check |
| --- | --- |
| 1 | Every requirement in the feature spec has a passing check (code, eval or manual). |
| 2 | Acceptance criteria in the spec pass. |
| 3 | The feature works on a readable link and on an unreadable link. |
| 4 | An error shows a clear message in plain English, not a crash. |
| 5 | The API key is not in any new file, log line or page. |
| 6 | Cost limits still apply: `max_tokens` and a maximum page length (NF-02). |
| 7 | Bookmarks are read and written only through `mnemo/core/store.py` (NF-03). |
| 8 | A guess is marked as a guess (NF-04). |
| 9 | The [smoke checklist](../testing/smoke-checklist.md) passes. |
| 10 | The change is committed, with a note in the session log. |
| 11 | Docs that describe the feature are updated. |

## Per phase
| Phase | Done when |
| --- | --- |
| 0 | A script gets an answer from Claude; a second call with history shows memory; the key is in `.env` and not in git. |
| 1 | A page on your computer has a chat box and a bookmark page; 5 public links give readable cards; an unreadable page is saved as link only; you found no invented fact. |
| 2 | One command scores 20 saved pages and prints three numbers; baseline ran twice; you read 3 results. |
| 3 | 3 or more prompt versions compared, one change at a time; Route set scored; unsure links go to Unsorted; Move and Undo work; tried on 10 real saves. |
| 4 | 15 questions and 3 trick questions run; every tool call gets a result; trick questions return "nothing found"; import works in small batches; screenshots save. |
| 5 | Retrieval eval compares BM25 alone, BM25 with RRF, and Claude picking; 5 planted duplicates caught. |
| 6 | A PDF is saved; an answer shows a quote that exists in the page text. |
| 7 | You accept or reject each proposed folder; nothing moves without your yes; a table compares single prompt, chain, parallel and review. |
| 8 | Digest runs on your list; every roast number equals the code count; cache fields read; thinking kept or dropped by the eval. |
| 9 | Inspector tests pass; Claude Code finds a bookmark. |
| 10 | Optional: one of dead-link doctor, CSV chart, or replacement search works. |
| A | Server online with login and spending cap; chat works in the iPhone browser. |
| B | Share from the iPhone reaches the server and the card appears. |
| C | A `.deb` file installs and opens the chat page in its own window. |

## What "done" does not mean
- A high eval score is not enough. See the [two-week user test](../testing/two-week-user-test.md).
- Code that runs once is not enough. Run it twice, with a bad input.

Related: [test strategy](../testing/test-strategy.md), [phases overview](../product/phases-overview.md).
