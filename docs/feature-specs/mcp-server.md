# MCP server (use from Claude Code)

Status: Draft v0.1 · Owner: KhoiTran · Phase: 9

This file describes the MCP server (MCP is a standard way for an AI tool to call your program) that lets Claude Code search your bookmarks.

## Purpose

While you work, Claude Code can ask "what do I already have about this?" Supports F-17 and job 3 of the plan.

## Scope

In: tools, resources, prompt, tests, client.
Out: the web server endpoints ([server-api.md](server-api.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| MC-01 | `mcp_server.py` is built with the Python SDK. |
| MC-02 | Tools: `search_bookmarks`, `add_bookmark`, `get_bookmark`. |
| MC-03 | A direct resource lists bookmarks. |
| MC-04 | A templated resource returns one bookmark. |
| MC-05 | A prompt named `find_related_to_task`. |
| MC-06 | All reads and writes go through the web server's HTTP API, which uses `store.py` ([storage.md](storage.md), [server-api.md](server-api.md)). The MCP server never opens `data/` itself (D-022). |
| MC-07 | `mcp_client.py` is used in the app. Then the server is added to Claude Code. |
| MC-08 | The server holds no more access than needed. It returns bookmarks, not the API key. |

## Behavior and rules

| Part | What it does |
| --- | --- |
| `search_bookmarks` | Search, same engine as the app ([search-no-embeddings.md](search-no-embeddings.md)). Returns at most 3. |
| `add_bookmark` | Saves a link like the chat does. Uses the same rules (honest failure, filing). |
| `get_bookmark` | One bookmark by number |
| Resource: list | All bookmarks (summary level) |
| Resource: one | One bookmark by id |
| Prompt `find_related_to_task` | Takes a task description and asks Claude Code to look for related bookmarks. Wording: Open question. |

- Private bookmarks (F-19): Open question whether they appear.
- `add_bookmark` calls the API and costs money. Cost limits (NF-02) still apply.

## Edge cases

| Case | Behavior |
| --- | --- |
| Bookmark id not found | Clear error result. |
| Search returns nothing | "nothing found". |
| `add_bookmark` gets an unreadable page | Saves link only; says so. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | Each tool, resource and prompt is tested in the MCP Inspector (a test tool for MCP servers). |
| 2 | Claude Code finds a bookmark you know exists. |
| 3 | A trick query returns "nothing found". |
| 4 | `add_bookmark` writes a record that passes validation. |

## Tests

Inspector tests listed in the phase 9 plan. Questions: [ask-golden-set.md](test-cases/ask-golden-set.md).

## Open questions

- Prompt text.
- Whether private bookmarks are visible.
- How Claude Code is told where the server is.
