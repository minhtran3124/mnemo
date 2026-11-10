# Weekly digest and roast

Status: Draft v0.1 · Owner: KhoiTran · Phase: 8

This file describes the weekly digest and the roast. Code does the counting; Claude writes only words.

## Purpose

Give something back every week (product rule 4). Supports F-14 and F-15.

## Scope

In: digest content, candidate rules, near-duplicates, dead links, roast numbers, temperature, caching.
Out: dead-link fixes by an agent (F-18, phase 10).

## Requirements

| ID | Requirement |
| --- | --- |
| DR-01 | The digest has three things to read, near-duplicates and dead links, in one short report. |
| DR-02 | Code picks the three candidates: never opened, oldest first, close to your recent questions. |
| DR-03 | Claude writes only the "why now" line for each candidate. |
| DR-04 | Code finds near-duplicates and dead links. |
| DR-05 | Every number in the roast comes from code. The model writes only the words around them. |
| DR-06 | The roast uses a personality system prompt and a higher temperature than other calls. |
| DR-07 | A cache breakpoint is placed on the long list. |
| DR-08 | Extended thinking is tried on `folders` only, and kept only if the eval gains. |

## Behavior and rules

Plan example (invented text):

```text
Read next (3):  #17, #8, #52
Looks like duplicates:  #12 and #31
Dead links (2):  #4, #22
Roast: You saved 14 articles about caching and opened none.
```

- The roast must make a real fact funny, never invent one. Check: every number in the text equals the code count.
- Open question: what counts as a dead link (which status codes), and how often to check.
- Open question: who triggers the digest (a button or a schedule).
- Caching: read `cache_creation_input_tokens` and `cache_read_input_tokens`. Unverified: minimum length for caching. Keep it only if numbers show a gain.
- Opened items are logged so the measure "share of read-next items opened" can be computed ([data-model.md](data-model.md)).
- Private bookmarks (F-19): kept out of the roast text. Open question.

## Edge cases

| Case | Behavior |
| --- | --- |
| Fewer than 3 unopened bookmarks | Show what exists. |
| No near-duplicates or dead links | Say "none". |
| Roast with numbers that do not match | Reject and retry. |
| Empty list | Short message, no roast. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | The digest runs on your list and shows the three parts. |
| 2 | Every roast number equals the code count (automatic check). |
| 3 | The candidate rule is tested with a fixed list. |
| 4 | Cache fields are read and written in the run log. |
| 5 | Thinking is kept or dropped by an eval result, written down. |

## Tests

Unit tests for candidate choice and counts. Near-duplicate logic: [duplicates.md](duplicates.md).

## Open questions

- Dead link definition.
- Digest trigger.
- Roast tone limits.
