# Privacy and security

Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file states what leaves your machine and how the key and the server are protected.

Visual page: [Architecture](https://claude.ai/artifact/HRJ54QxYXpooHoemp6uSgV). It is a snapshot of `main` at commit `ce40e28` and is private until you share it. This file is the source of truth; if they differ, fix the page.

## Purpose

Supports NF-01 (key only on the server), NF-02 (cost limits), F-11 and F-19.

## Scope

In: data flow, key, binding, login, spending cap, private mode, policy.
Out: legal advice. The plan says: I am not a lawyer.

## Requirements

| ID | Requirement |
| --- | --- |
| PV-01 | The API key is in `.env` on the server, never in a web page, an app or git (NF-01). |
| PV-02 | Local server binds to `127.0.0.1`, never `0.0.0.0`. |
| PV-03 | The online server (phase A) needs a login, a `max_tokens` limit, a maximum page length and a spending cap (NF-02). |
| PV-04 | Public links only while building (D-018). |
| PV-05 | Check your company's AI policy before saving work links. |
| PV-06 | Private mode (F-19, D-017, accepted): a link marked private is saved as link only and nothing is sent to the API. |
| PV-07 | Never print the key (project rule in `CLAUDE.md`). |

## What leaves the machine

With the Claude API only, these go to Anthropic: page text, the URL and your questions. Storage can stay local. The server also fetches pages from the internet.

| Item | Goes to |
| --- | --- |
| Page text, URL, questions | Anthropic API |
| Page requests | The websites you save |
| Bookmark files | Stay on your disk (local phase) |
| Saved page text | Stays on your disk; do not share it |

Unverified: Anthropic's data retention policy for the API. Read it before saving anything private. Open question: retention settings.

## Behavior and rules

- Local first (D-007). In phase A the host holds the files too. Host storage and rules: Unverified, see [storage.md](storage.md).
- A public server can spend your money if someone finds it. Do not skip the login.
- Set a monthly spending limit in the Claude Console. Unverified: whether your account offers a cap.
- Private mode: write `private <link>` in the chat. Plain code reads the prefix, so the app fetches no page text and makes no Claude call. The bookmark keeps `private` = true and a null summary. The link and its title stay local; `private` with no link is a question, not a save. Details of what remains searchable: Open question.
- Share endpoint token: see [server-api.md](server-api.md).

## Edge cases

| Case | Behavior |
| --- | --- |
| Link looks like an internal company site | Open question: warn before saving. |
| `.env` committed by mistake | Rotate the key at once. See [git-and-secrets.md](../process/git-and-secrets.md). |
| Spending cap reached | Server refuses new Claude calls, saves link only. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | `.gitignore` lists `.env`; a search of the repo finds no key. |
| 2 | The local server is not reachable from another device on the network. |
| 3 | The online server refuses calls without login or token. |
| 4 | Page source of the web pages contains no key. |
| 5 | A private link produces no API call (log check). |

## Tests

Manual checks in `testing/`.

## Open questions

- Company AI policy result.
- Retention policy.
- Whether private bookmarks appear in the digest, the MCP server and search (see [digest](digest-and-roast.md), [MCP server](mcp-server.md), [search](search-no-embeddings.md)). The save behaviour itself is decided: [chat and intent](chat-and-intent.md).
