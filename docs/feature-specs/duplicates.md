# Duplicates: "Do I have this?"

Status: Draft v0.1 · Owner: KhoiTran · Phase: 5

This file describes the warning shown when you save a link you already have, or something close to it.

## Purpose

Stop you from collecting copies. Supports F-09. Your sample list already has one exact duplicate.

## Scope

In: URL cleaning, exact duplicate, near-duplicate, warning texts, tests.
Out: near-duplicate list in the weekly digest ([digest-and-roast.md](digest-and-roast.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| DU-01 | Code cleans the URL before any comparison. |
| DU-02 | Same cleaned URL means exact duplicate. |
| DU-03 | A candidate that Claude says is the same page, or about the same news, means near-duplicate. |
| DU-04 | The two cases have different warning texts. |
| DU-05 | A warning never blocks a save. You decide. |

## URL cleaning rules

| Rule | Example |
| --- | --- |
| Remove `fbclid` | long Facebook tracking part |
| Remove `utm_*` parameters | `utm_source` and others |
| Other parameters, a trailing slash, `www`, upper or lower case | Open question: the plan lists only `fbclid` and `utm_*`. |

Reference: [url-cleaning.md](../solutions/url-cleaning.md). The cleaned link is stored as `url_clean` (proposed, see [data-model.md](data-model.md)).

## Behavior and rules

- Exact: compare `url_clean` with all saved bookmarks. Code only, no API call.
- Near: use the search of phase 5 to get candidates. Claude is asked if a candidate is the same page or the same story. This is a guess, so the text says "similar".

| Case | Warning text |
| --- | --- |
| Exact | "You saved this already" (with the earlier bookmark and its save date) |
| Near | "You saved something similar" (with the earlier bookmark) |

Final wording: Open question.

## Edge cases

| Case | Behavior |
| --- | --- |
| Same repo, link with `fbclid` | Exact duplicate. |
| Two articles on the same Brotli flaw (thehackernews.com and bleepingcomputer.com) | Near-duplicate. The bleepingcomputer fetch may fail, so only the link may be known. Open question: how to compare then. |
| Different pages on one site | Not duplicates. |
| Unreadable page | Only exact check is possible. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | Unit tests for cleaning: a link with `fbclid` or `utm_*` equals the clean link. |
| 2 | 5 planted duplicates are caught (phase 5 done-check). |
| 3 | An exact duplicate shows the exact text; a near-duplicate shows the near text. |
| 4 | A new, different link shows no warning. |

## Tests

[hard-cases.md](test-cases/hard-cases.md) (repeat link, Brotli pair). Sources: [sample-links.md](../reference/sample-links.md).

## Open questions

- Full cleaning list.
- How Claude judges "same story" and how sure it must be.
- Warning wording.
