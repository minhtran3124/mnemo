# Classification and filing

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, 3

This file describes what Claude returns for each save, and how the result becomes a filed bookmark.

## Purpose

One Claude call turns page text into type, tags, summary, reason and a folder choice. Code checks every part. Supports F-01, F-03, NF-04.

## Scope

In: type list, tag and summary rules, reason, faithful-summary rule, output contract, filing choice.
Out: folder rules in detail (see [folders.md](folders.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| CF-01 | `type` is one value from the type list. |
| CF-02 | 3 to 6 tags, all lowercase. |
| CF-03 | Summary is at most 60 words. |
| CF-04 | `reason_source` is `user` if you typed a reason, `guess` if Claude wrote it. |
| CF-05 | The summary has only facts that are in the page text (NF-04). |
| CF-06 | Claude returns clean JSON. Code parses and validates it. |
| CF-07 | The folder is one existing folder name or `Unsorted`. |

## Type list

`github_repo`, `article`, `video_page`, `tool`, `pdf`, `image`, `note`. Proposed (D-013, not built): `docs` for API reference pages, `other` for index pages and unclear pages. Without them, two sample links get a wrong type. An arXiv paper is `article` with the tag `paper`. Whether this confuses the eval: Open question.

## Behavior and rules

- Reason: optional, one line. If missing, Claude writes a guess and `reason_source` = `guess`. The card shows "guess".
- Faithful-summary rule: if the page text does not say it, the summary does not say it. A screenshot post that claims "Anthropic published this" is reported as "the post claims it" or left out.
- Page text is placed inside XML tags in the prompt. Instructions are outside them.
- Prompts live in `mnemo/save/prompts/`, one file per version. Change one thing per run (phase 3).

### Claude output contract

| Part | Rule |
| --- | --- |
| Format | One JSON object: `type`, `title`, `summary`, `tags`, `reason`, `folder`. |
| How | Structured outputs (D-025): `client.messages.parse(output_format=<Pydantic model>)`, result in `response.parsed_output`. No prefill, no stop sequence, no beta header. `claude-haiku-5-5` supports it ([docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), checked in api-notes item 13). |
| What the API cannot enforce | `minLength`, `maxLength`, `maxItems` and number limits are not supported in the schema. Code checks 3 to 6 distinct lowercase tags and 60 words itself; `type` is a literal of the allowed values in the schema (CF-02, CF-03, DM-02). |
| Bad stop reason | `refusal` and `max_tokens` can give output that does not match the schema. Treat both as invalid: retry once, then save link only. |
| Temperature | Not set. `Messages.create()` in `anthropic` 2.4.0 has no `temperature` parameter. |
| Limits | Structured outputs cannot be combined with citations (400 error). Phase 6 quotes need another way ([api-notes](../reference/api-notes.md) item 13). |

### Filing choice

Claude picks from the folders that exist, or `Unsorted`. If unsure, it must choose `Unsorted`. Code rejects any other name: the bookmark is stored with `folder` = null (Unsorted) and one `folder_rejected` line is written to `log.jsonl` with the rejected name. Details: [folders.md](folders.md).

## Edge cases

| Case | Behavior |
| --- | --- |
| Invalid output (schema mismatch, `refusal`, `max_tokens`) | One retry. Then save link only and say so. |
| Transient API error (connection, timeout, 429, 5xx, 408, 409, 529) | One retry. Then save link only. Logged once per retry and per fallback with the exception class and status code. |
| Permanent API error (400, 401, 403, 404, other 4xx) or missing API key | Do not retry and do not swallow. The error propagates, so a revoked key never looks like an unreadable page. See [honest-failure.md](../solutions/honest-failure.md). |
| Tags repeat after lowercasing | Duplicates are dropped before the 3 to 6 count. |
| Tag count is 2 or 7 | Reject. Retry once. |
| Summary is 61 words | Reject. Retry once. |
| Unreadable page | No Claude call for a summary. `summary` = `null`. |
| Private link (F-19) | No Claude call at all. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | Code check passes for JSON, tags, summary length (see the checks table in [save-golden-set.md](test-cases/save-golden-set.md)). |
| 2 | Faithful-summary grader finds 0 unsupported statements. |
| 3 | Type matches expected type on the Save set. Target: set after first baseline. |
| 4 | Filing: the Route set scores the folder choice ([route-set.md](test-cases/route-set.md)). |

## Tests

[save-golden-set.md](test-cases/save-golden-set.md), [route-set.md](test-cases/route-set.md).

## Open questions

- Whether `docs` and `other` are added.
- Passing score for each check.
- Whether you really type the reason (checked after phase 3).
