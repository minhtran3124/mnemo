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
| `POST /api/chat` | Send a message. Code decides link or question. | `message`, optional `pasted_text` | A card, or an answer with up to 3 bookmarks |
| `GET /api/bookmarks` | List bookmarks | Optional `folder`, `type`, `tag`, `q` | List of records ([data-model.md](data-model.md)) |
| `PATCH /api/bookmarks/:id` | Move to another folder (phase 3) | `folder` | Updated record. Rejects unknown folder |
| `POST /api/bookmarks/:id/undo` | Undo last filing or move (phase 3) | none | Updated record |
| `DELETE /api/bookmarks/:id` | Delete | none | Confirmation |
| `POST /api/import` | Start or continue an import | File or pasted text; `stage` (estimate, run) | Count, cost estimate, batch result |
| `POST /api/share` | Save from the iPhone Shortcut | `url`, token | Same card data as chat |
| `GET /api/folders` | List folders with counts | none | List of folders |

Open question: how `open` is logged (a path or a log call), and the upload endpoint for PDFs and screenshots.

## Auth

- Token: a long random value kept in `.env` on the server and in the Shortcut or browser. Header name: Open question.
- Phase A also adds a login for the web page. The token must never be in a public repo ([git-and-secrets.md](../process/git-and-secrets.md)).

## Error format (proposed)

```json
{ "error": { "code": "folder_not_found", "message": "Folder does not exist." } }
```

| Status | Use |
| --- | --- |
| 400 | Bad input (for example unknown folder) |
| 401 | Missing or wrong token |
| 404 | Unknown bookmark |
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

## Tests

Automated tests for each endpoint. Phone test: `manual-testing`.

## Open questions

- Header name and token handling.
- Upload endpoint.
- Pagination for long lists.
