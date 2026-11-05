# Storage (`store.py`)

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, A

This file describes the one module that reads and writes bookmarks.

Visual page: [Data model](https://claude.ai/artifact/RjucLkUNCY5pWzD3RxJkpt). It is a snapshot of `main` at commit `ce40e28` and is private until you share it. This file is the source of truth; if they differ, fix the page.

## Purpose

All access to bookmarks goes through `store.py` (NF-03, D-012). Then the inside can change from files to a database and nothing else changes.

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
| ST-05 | `store.py` validates records before writing ([data-model.md](data-model.md)). |

## Interface

| Function | Purpose |
| --- | --- |
| `add_bookmark(record, page_text=None)` | Validate and add; the server sets `id`, `saved_at` and `page_file`; write the page file |
| `get_bookmark(id)` | Return one record |
| `list_bookmarks(filters)` | Return records in saved order; filters `folder`, `type`, `tag` |
| `update_bookmark(id, fields)` | Change fields (for example folder) and validate again; `id`, `saved_at` and `page_file` cannot change |
| `delete_bookmark(id)` | Remove record and page file |
| `read_page(id)` | Return saved page text, or `None` if the file is missing |
| `list_folders()` | Named folders with counts (`{folder, count}`); Unsorted is not listed |
| `log_event(event)` | Append a line to `log.jsonl`; the server adds `time` (UTC) |
| `append_chat(message)` | Append a line to `chat.jsonl`; the server sets `id` (counts on from the last line) and `time` (UTC) |
| `list_chat(limit)` | Return the latest chat messages, oldest first |
| `find_by_url_clean(url)` | Used by the duplicate check |

Errors: `InvalidRecord` (a `ValueError`) for a bad record, `NotFound` for an unknown id, `StoreError` for a corrupt file. All three share the base `StoreError`. The point is a small, fixed surface.

## Behavior and rules

- Files: `data/bookmarks.json`, `data/pages/<id>.txt`, `data/chat.jsonl`, `data/log.jsonl`.
- `bookmarks.json` is `{"next_id": n, "bookmarks": [...]}`. `next_id` only goes up, so an ID is never reused, even after a delete.
- `DATA_DIR` in `store.py` is read at call time, so tests point it at a temp folder.
- Undo needs the previous folder to be remembered. Open question: where it is kept (a field or the log).
- Backup: copy `data/` regularly. How and how often: Open question. Keep backups out of git if they contain page text.

### Database swap

Phase A: you plan to use Render. Unverified: Render price and whether its disk keeps files between deploys. Check before phase A ([hosting-check.md](../research/hosting-check.md)). If the disk is not persistent, replace the inside of `store.py` with a database and change nothing else. The budget in the plan is about $10 per month for hosting and the API together (unverified prices).

## Edge cases

| Case | Behavior |
| --- | --- |
| Crash during a write | Old file is still whole (atomic write). |
| Two writes at once | Open question: a lock, or one worker only. |
| Missing page file | `read_page` returns nothing; the record stays. |
| Torn last line in `chat.jsonl` or `log.jsonl` (crash during append) | Torn means the file ends without a newline. Reads skip it; the next append cuts it off first. A bad line that ends with a newline, or sits anywhere else, raises `StoreError`. |
| Corrupt `bookmarks.json` | `store.py` raises `StoreError` with a clear message and never overwrites the file; restore from backup. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | A search of the code finds no direct open of `data/` outside `store.py`. |
| 2 | A test that kills the process during a write leaves a valid file. |
| 3 | An invalid record is rejected. |
| 4 | A backup can be restored in a test. |
| 5 | Swapping to a database (when needed) passes the same store tests. |

## Tests

Unit tests per function. A shared test set can run against both file and database versions.

## Open questions

- Render disk behavior and price.
- Backup method.
- Lock for two writers.
