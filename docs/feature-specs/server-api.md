# Server API (proposed design)

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, A, B

This file proposes a small set of HTTP endpoints for the web pages. It is a proposed design, not yet built. Names and fields may change.

Visual page: [Architecture](https://claude.ai/artifact/HRJ54QxYXpooHoemp6uSgV). It is a snapshot of `main` at commit `ce40e28` and is private until you share it. This file is the source of truth; if they differ, fix the page.

## Purpose

The screens are thin and call one Python server. The server holds the key (NF-01, D-002). Supports F-04, F-11, F-12.

## Scope

In: endpoint list, fields, auth token, error format.
Out: the MCP interface ([mcp-server.md](mcp-server.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| SA-01 | All data access goes through `store.py` ([storage.md](storage.md)). |
| SA-02 | The server never returns the API key. |
| SA-03 | From phase A (and phase B), every call needs a token. On the local server in phase 1 there is no login yet. |
| SA-04 | Errors use one format. |

## Endpoints (proposed)

| Method and path | Purpose | Request | Response |
| --- | --- | --- | --- |
| `POST /api/chat` | Send a message. Code decides: save a link, edit a reason (`note <id> <text>`), or answer a question. Both sides of the exchange are appended to the chat history. | `message`, optional `pasted_text` | A card, a confirmation, or an answer with up to 3 bookmarks |
| `GET /api/chat/history` | Return the saved chat so the page can redraw it after a reload | Optional `limit` (default 50) | List of chat messages ([data-model.md](data-model.md)) |
| `GET /api/bookmarks` | List bookmarks in saved order | none in phase 1 (filters `folder`, `type`, `tag`, `q` come later) | List of records ([data-model.md](data-model.md)) |
| `PATCH /api/bookmarks/:id` | Change a bookmark: the reason (phase 1, from `note <id> <text>`; sets `reason_source` to `user`) or the folder (Move, phase 3) | `reason` or `folder` | Updated record. Rejects an unknown folder or an unknown id |
| `POST /api/bookmarks/:id/open` | Record that a link was opened: `opened_count` goes up and an `open` line is logged. The page opens `url_clean` itself in a new tab and sends this call in the background, so a pop-up blocker cannot stop the link. | none | Updated record. Unknown id gives 404 `bookmark_not_found`. The count change runs under a server lock, so parallel opens are all counted |
| `POST /api/bookmarks/:id/paste` | Fill in an unreadable bookmark from pasted text. The same bookmark is updated (id, `saved_at`, `opened_count`, folder and a user-written reason are kept); `page_status` becomes `ok`. The Claude call runs outside the server lock, the store write inside it | `text` | Updated record. Unknown id gives 404 `bookmark_not_found`; a bookmark that is not unreadable gives 409 `already_read`; text under the pasted-text floor gives 400 `text_too_short`; invalid output after one retry gives 502 `summary_failed` and nothing changes. Auth and config errors propagate as in a normal save |
| `POST /api/bookmarks/:id/undo` | Undo last filing or move (phase 3) | none | Updated record |
| `DELETE /api/bookmarks/:id` | Delete the bookmark and its saved page text | none | `{"deleted": id}` with 200. Unknown id gives 404 `bookmark_not_found` |
| `POST /api/import` | Start or continue an import | File or pasted text; `stage` (estimate, run) | Count, cost estimate, batch result |
| `POST /api/share` | Save from the iPhone Shortcut | `url`, token | Same card data as chat |
| `GET /api/folders` | List folders with counts | none | List of folders |

Open question: filters on `GET /api/bookmarks` (`folder`, `type`, `tag`, `q`) are not built yet; decide with the search work.

Open question: the upload endpoint for PDFs and screenshots.

## Auth

- Token: a long random value kept in `.env` on the server and in the Shortcut or browser. Header name: Open question.
- Phase A also adds a login for the web page. The token must never be in a public repo ([git-and-secrets.md](../process/git-and-secrets.md)).

## Start command

`uv run python server.py` starts the server on `127.0.0.1` (`HOST` in `server.py`). It never binds to another address.

## POST /api/chat in phase 1

- Request: `message` (required) and optional `pasted_text`. `pasted_text` applies only to the first link in the same message.
- A blank or whitespace-only `message` returns 400 with code `empty_message`.
- A message with one or more distinct links saves each in order (links with the same `url_clean` are saved once) and returns `{"kind": "cards", "cards": [record, ...]}`. If a link fails to store (a `StoreError` or `OSError`) after another saved, the response is still 200 with the saved cards plus `"failed": [link, ...]`, so a retry does not save them twice. If no link saved, the response is the usual 500. Missing key, auth and other errors are never put in `failed`: they return the usual JSON 500.
- A message with no link returns `{"kind": "text", "text": "I can only save links for now. Asking comes later."}`. Nothing is sent to Claude.
- Phase 1 appends nothing to the chat history here. History is its own ticket. `note <id> <text>` is also its own ticket.

## Error format (proposed)

```json
{ "error": { "code": "folder_not_found", "message": "Folder does not exist." } }
```

| Status | Use |
| --- | --- |
| 400 | Bad input (for example unknown folder, or a request that fails validation; code `bad_request`; a blank chat message; code `empty_message`) |
| 401 | Missing or wrong token |
| 409 | The bookmark is not unreadable (code `already_read`) |
| 404 | Unknown bookmark (code `bookmark_not_found`) or unknown route (code `not_found`) |
| 502 | Claude gave invalid output twice on a paste fill-in (code `summary_failed`) |
| 429 | Spending cap or rate limit reached |
| 500 | Server error |

## Edge cases

| Case | Behavior |
| --- | --- |
| Share endpoint gets no URL | 400. |
| Page cannot be read | 200 with a "Page not read" card, not an error. |
| Spending cap hit | 429 and a clear message. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | Each endpoint returns the fields above for a happy path. |
| 2 | Missing token gives 401 (from phase A). |
| 3 | A move to an unknown folder gives 400. |
| 4 | No response contains the API key. |
| 5 | After a save and a reload, `GET /api/chat/history` returns the earlier messages, and each card is built from the bookmark record. |
| 6 | `POST /api/bookmarks/:id/open` raises `opened_count` by 1 and writes one `open` log line. |
| 7 | `PATCH` with a `reason` changes the reason and sets `reason_source` to `user`; an unknown id gives 404. |
| 8 | `DELETE /api/bookmarks/:id` returns `{"deleted": id}` and removes the record and its page file; an unknown id gives 404 `bookmark_not_found`. |

## Tests

Automated tests for each endpoint. Phone test: `manual-testing`.

## Open questions

- Header name and token handling.
- Upload endpoint.
- Clearing the chat history (not in phase 1).
- Pagination for long lists.
