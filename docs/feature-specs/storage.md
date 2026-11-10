# Storage (`mnemo/core/store.py`)

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, A

This file describes the one module that reads and writes bookmarks.

Visual page: [Data model](https://claude.ai/artifact/RjucLkUNCY5pWzD3RxJkpt). It is a snapshot of `main` at commit `ce40e28` and is private until you share it. This file is the source of truth; if they differ, fix the page.

## Purpose

All access to bookmarks goes through `mnemo/core/store.py` (NF-03, D-012). Then the inside can change from files to a database and nothing else changes.

## Scope

In: function list, JSON files now, database swap, atomic writes, backups.
Out: the record shape ([data-model.md](data-model.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| ST-01 | No other module opens `data/` files directly. |
| ST-02 | Storage is plain JSON and text files in version 1. No database. |
| ST-03 | Writes are atomic: write a temporary file, then rename it, so a crash cannot leave half a file. |
| ST-04 | Data is backed up. |
| ST-05 | `mnemo/core/store.py` validates records before writing ([data-model.md](data-model.md)). |

## Interface

| Function | Purpose |
| --- | --- |
| `add_bookmark(record, page_text=None)` | Validate and add; the server sets `id`, `saved_at` and `page_file`; write the page file |
| `get_bookmark(id)` | Return one record |
| `list_bookmarks(filters)` | Return records in saved order; filters `folder`, `type`, `tag` |
| `update_bookmark(id, fields)` | Change fields (for example folder) and validate again; `id`, `saved_at` and `page_file` cannot change |
| `update_bookmark_with_page(id, fields, page_text)` | Like `update_bookmark`, and write the page file after the record validates; remove the page file again if the record cannot be saved. Used to fill in an unreadable bookmark |
| `delete_bookmark(id)` | Remove record and page file |
| `read_page(id)` | Return saved page text, or `None` if the file is missing |
| `list_folders()` | Named folders with counts (`{folder, count}`); Unsorted is not listed |
| `log_event(event)` | Append a line to `log.jsonl`; the server adds `time` (UTC) |
| `append_chat(message)` | Append a line to `chat.jsonl`; the server sets `id` (highest id plus 1) and `time` (UTC). An optional `failed` list of URL strings is kept as given (see `data-model.md`) |
| `list_chat(limit)` | Return the latest chat messages, oldest first |
| `find_by_url_clean(url)` | Used by the duplicate check |

HTTP route `PATCH /api/bookmarks/{id}` takes `{"reason": "<text>"}` or `{"folder": "<name>"}`. A reason sets `reason` and `reason_source` to `user`; a folder moves the bookmark and copies the old folder to `prev_folder`. It returns the updated record. An unknown folder gives 400 (`folder_not_found`). A missing, empty or blank reason gives 400 (`empty_reason`, or `bad_request` for a bad body). An unknown id gives 404 `bookmark_not_found`. The chat command `note <id> <text>` uses the same reason path. `POST /api/bookmarks/{id}/undo` restores `prev_folder` and clears it; 409 (`nothing_to_undo`) when `prev_folder` is null.

Errors: `InvalidRecord` (a `ValueError`) for a bad record, `NotFound` for an unknown id, `StoreError` for a corrupt file or a line in `chat.jsonl` or `log.jsonl` that is not JSON. All three share the base `StoreError`. The point is a small, fixed surface.

## Behavior and rules

- Files: `data/bookmarks.json`, `data/pages/<id>.txt`, `data/chat.jsonl`, `data/log.jsonl`.
- `data/pages/<id>.txt` holds the same text Claude was given: whitespace collapsed once, cut to `MAX_PAGE_CHARS` once. Pasted text under 40 characters is not stored (link only).
- `bookmarks.json` is `{"next_id": n, "bookmarks": [...]}`. `next_id` only goes up, so an ID is never reused, even after a delete.
- `DATA_DIR` in `mnemo/core/store.py` is read at call time, so tests point it at a temp folder.
- Undo is one step: a Move or a filing copies the old folder to `prev_folder` (with `Unsorted` stored as the string `Unsorted`), and Undo restores it and clears the field. A null `prev_folder` means there is nothing to undo.
- Backup: copy `data/` regularly. How and how often: Open question. Keep backups out of git if they contain page text.

### Database swap

Phase A: you plan to use Render. Checked on the [Render disks page](https://render.com/docs/disks): a disk keeps files across deploys and restarts, but only under its mount path, only on a paid service, and for one instance. Unverified: the price (the page lists none). See [hosting-check.md](../research/hosting-check.md). If the disk ever stops fitting, replace the inside of `mnemo/core/store.py` with a database and change nothing else. The budget in the plan is about $10 per month for hosting and the API together (unverified prices).

## Edge cases

| Case | Behavior |
| --- | --- |
| Crash during a write | Old file is still whole (atomic write). |
| Two writes at once | One process-local write lock in the web server (D-035). The web server is the only writer; the MCP server calls its HTTP API (D-022). |
| Missing page file | `read_page` returns nothing; the record stays. |
| Bad line in `chat.jsonl` or `log.jsonl` | `mnemo/core/store.py` raises `StoreError`. There is no crash recovery for a half-written line. Chat lines are never deleted, so the next chat `id` is the highest `id` in the file plus 1. |
| Corrupt `bookmarks.json` | `mnemo/core/store.py` raises `StoreError` with a clear message and never overwrites the file; restore from backup. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | A search of the code finds no direct open of `data/` outside `mnemo/core/store.py`. |
| 2 | A test that kills the process during a write leaves a valid file. |
| 3 | An invalid record is rejected. |
| 4 | A backup can be restored in a test. |
| 5 | Swapping to a database (when needed) passes the same store tests. |

## Tests

Unit tests per function. A shared test set can run against both file and database versions.

## Open questions

- Render disk price.
- Backup method.
- A cross-process lock in `mnemo/core/store.py`: needed only if a second process ever writes files directly.
