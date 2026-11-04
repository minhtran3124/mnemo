# Data model

Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file fixes the shape of one bookmark record and the files in `data/`, so every phase reads and writes the same thing.

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

## The record

Example values only.

```json
{
  "id": 42,
  "url": "https://github.com/example/test-tool",
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
| `url` | string | The link as saved. Empty for a screenshot with no link (see [pdf-and-screenshots.md](pdf-and-screenshots.md)). |
| `saved_at` | string | ISO date and time, set by the server. |
| `type` | string | `github_repo`, `article`, `video_page`, `tool`, `pdf`, `image`, `note`. Proposed (D-013): `docs`, `other`. |
| `title` | string | Page title or a short title made from the text. |
| `page_status` | string | `ok` or `unreadable`. |
| `summary` | string or null | At most 60 words. `null` if unreadable. |
| `tags` | list of strings | 3 to 6 tags, all lowercase. Proposed limits: you can change them in phase 2. |
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
| `url_clean` | string | The link after tracking parts are removed. Used for duplicates (see [duplicates.md](duplicates.md)). |
| `language` | string | Not in version 1 (D-011). |

## Data layout

```text
data/
  bookmarks.json    all records
  pages/<id>.txt    saved page text, one file per bookmark
  log.jsonl         one JSON object per line, one per event
```

## log.jsonl event types

The plan names: saves, opens and digests. Each line has an event name and a time. Other fields: Open question: exact fields per event.

| Event | When |
| --- | --- |
| `save` | A bookmark is saved. Also records whether you typed only the link (user measure). |
| `open` | A link is opened from the app. |
| `digest` | A weekly digest is made. |

## Edge cases

- A page is unreadable: `summary` is `null`, `tags` may be empty only in this case. Open question: are 3 tags required for link-only bookmarks?
- A screenshot has no URL: `url` is empty.
- Claude returns an unknown `type`: code rejects it and uses `other` if D-013 is accepted, otherwise the save fails honestly.

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | Code rejects a record with a missing field, a bad `type`, or uppercase tags. |
| 2 | Code rejects an unreadable record that has a summary. |
| 3 | Code rejects a summary over 60 words. |
| 4 | After a save, `bookmarks.json`, `pages/<id>.txt` and one log line exist. |

## Tests

See [save-golden-set.md](test-cases/save-golden-set.md) for the checks table.

## Open questions

- Final tag and summary limits (decided in phase 2).
- Fields of each log event.
- Whether `docs` and `other` are added (D-013).
