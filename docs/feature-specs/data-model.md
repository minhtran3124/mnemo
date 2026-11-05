# Data model

Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file fixes the shape of one bookmark record and the files in `data/`, so every phase reads and writes the same thing.

Visual page: [Data model](https://claude.ai/artifact/RjucLkUNCY5pWzD3RxJkpt). It is a snapshot of `main` at commit `ce40e28` and is private until you share it. This file is the source of truth; if they differ, fix the page.

## Purpose

Every phase reads and writes the same bookmark record. If the record changes, all phases change. So we fix it now. Supports NF-03 (plain files) and D-012 (all access through `store.py`, see [storage.md](storage.md)).

## Scope

In: the record, allowed values, validation rules, file layout, log events.
Out: how the files are read and written (see [storage.md](storage.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| DM-01 | Every bookmark is one JSON object with the fields below. |
| DM-02 | Code validates a record before it is written. An invalid record is rejected, not repaired silently. |
| DM-03 | `summary` is `null` when `page_status` is `unreadable` (NF-04). |
| DM-04 | `folder` is `null` until a folder is accepted or filed (see [folders.md](folders.md)). |
| DM-05 | Page text is stored in its own file, not inside `bookmarks.json`. |
| DM-06 | Every chat message is appended to `data/chat.jsonl` and shown again after a reload. The history is never sent to Claude. |

## The record

Example values only.

```json
{
  "id": 42,
  "url": "https://github.com/example/test-tool?utm_source=x",
  "url_clean": "https://github.com/example/test-tool",
  "saved_at": "YYYY-MM-DDTHH:MM:SS",
  "type": "github_repo",
  "title": "test-tool",
  "page_status": "ok",
  "summary": "A command line tool that generates test data for forms.",
  "tags": ["testing", "python", "cli"],
  "reason": "for login test cases",
  "reason_source": "user",
  "folder": null,
  "opened_count": 0,
  "page_file": "data/pages/42.txt"
}
```

| Field | Type | Allowed values and rules |
| --- | --- | --- |
| `id` | integer | Unique. Never reused. |
| `url` | string | The link as the user pasted it. Empty for a screenshot with no link (see [pdf-and-screenshots.md](pdf-and-screenshots.md)). |
| `url_clean` | string | The link after `fbclid` and `utm_*` are removed ([url-cleaning.md](../solutions/url-cleaning.md)). Code uses it to fetch, to open and to find duplicates. Empty when `url` is empty. |
| `saved_at` | string | ISO date and time, set by the server. |
| `type` | string | `github_repo`, `article`, `video_page`, `tool`, `pdf`, `image`, `note`. Proposed (D-013): `docs`, `other`. |
| `title` | string | Page title or a short title made from the text. |
| `page_status` | string | `ok` or `unreadable`. |
| `summary` | string or null | At most 60 words. `null` if unreadable. |
| `tags` | list of strings | 3 to 6 tags, all lowercase. May be empty only when `page_status` is `unreadable`. Proposed limits: you can change them in phase 2. |
| `reason` | string | One line. May be empty. |
| `reason_source` | string | `user` or `guess`. |
| `folder` | string or null | An existing folder name, or `null`. |
| `opened_count` | integer | Starts at 0. Goes up when the link is opened from the app. |
| `page_file` | string | Path to the saved page text. |

An arXiv paper uses `type` = `article` with the tag `paper`.

## Proposed additions

| Field | Type | Purpose |
| --- | --- | --- |
| `private` | boolean | F-19, D-017. A private link is saved as link only. Nothing is sent to the API. |
| `source` | string | `chat`, `import`, `shortcut` or `screenshot`. |
| `language` | string | Not in version 1 (D-011). |

## Data layout

```text
data/
  bookmarks.json    all records
  pages/<id>.txt    saved page text, one file per bookmark
  chat.jsonl        one JSON object per line, one per chat message (the chat history)
  log.jsonl         one JSON object per line, one per event
```

### Chat message (one line of `chat.jsonl`)

The chat history is kept so the chat page shows the earlier messages and cards after a reload. It is for display only: it is never sent to Claude (each save is its own call).

```json
{ "id": 7, "time": "YYYY-MM-DDTHH:MM:SS", "role": "user", "text": "https://example.com/a for login tests", "bookmark_ids": [] }
```

| Field | Type | Rules |
| --- | --- | --- |
| `id` | integer | Unique, in order. Never reused. |
| `time` | string | ISO date and time, set by the server. |
| `role` | string | `user` or `app`. |
| `text` | string | What the user typed, or the app's message (for example "I could not read this page. I saved the link only."). |
| `bookmark_ids` | list of integers | The bookmarks a card or an answer refers to. The page draws the card from the bookmark record, so a card never goes stale. A deleted bookmark is shown as "deleted". |
| `failed` | list of strings | Optional. The links in the message that could not be saved. Only an app message has it, and only when at least one link failed. `GET /api/chat/history` returns it, so the page draws "I could not save this link." after a reload. |

## log.jsonl event types

The plan names: saves, opens and digests. Each line has `event` and `time` (ISO date and time, set by the server). The other fields below are the starting set for phase 1; later phases may add more.

| Event | When | Other fields |
| --- | --- | --- |
| `fetch` | One fetch attempt for a page (so a retry can be checked in the log) | `url_clean`, `attempt` (1 or 2), `outcome` (`ok`, `timeout`, `error`, `too_short`, `blocked`), `ms` |
| `save` | A bookmark is saved. | `id`, `url_clean`, `page_status`, `typed_only_link` (true if the message was only the link), `tokens_in`, `tokens_out` |
| `open` | A link is opened from the app. | `id` |
| `digest` | A weekly digest is made (phase 8). | Open question |

## Edge cases

- A page is unreadable: `summary` is `null`, `tags` may be empty only in this case (decided: 3 tags are not required for link-only bookmarks).
- A screenshot has no URL: `url` is empty.
- Claude returns an unknown `type`: code rejects it and uses `other` if D-013 is accepted, otherwise the save fails honestly.

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | Code rejects a record with a missing field, a bad `type`, or uppercase tags. |
| 2 | Code rejects an unreadable record that has a summary. |
| 2b | Code accepts an unreadable record with no tags, and rejects a readable record with fewer than 3 tags. |
| 3 | Code rejects a summary over 60 words. |
| 4 | After a save, `bookmarks.json`, `pages/<id>.txt` and one log line exist. |

## Tests

See [save-golden-set.md](test-cases/save-golden-set.md) for the checks table.

## Open questions

- Final tag and summary limits (decided in phase 2).
- Fields of the `digest` log event.
- Whether `docs` and `other` are added (D-013).
