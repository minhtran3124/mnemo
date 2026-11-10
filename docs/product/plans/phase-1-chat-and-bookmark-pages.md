# Phase 1: Chat and Bookmark Pages
Status: Draft v0.1 · Owner: KhoiTran · Phase: 1

Build the first working app: paste a link in a chat page, get a card, and see the saved list on a second page.

## Goal
F-01 (save), F-02 (honest failure), F-04 (two screens), F-05 (Grid and List views).

## You can now
Paste a link in a chat page and get a card. See the saved list on the bookmark page.

## Sessions and lessons
3 sessions. Lessons 3-8, 16, 17.

## Inputs
Phase 0 done. The 5 test links in [sample links](../../reference/sample-links.md), section "Phase 1 test set", including one unreadable page (an X post).

## Tasks
Each task is one change with its own check, so each can become one ticket. Tasks 1 to 3 repair and extend what phase 0 built. Do them first.

**Foundation (phase 0 follow-up)**
1. Fix `client.ask()`: remove the `temperature` argument. `Messages.create()` in the installed `anthropic` 2.4.0 has no such parameter, so a caller that passes it gets `TypeError`. The phase 0 tests used a fake SDK and missed it. Add a test that checks the keyword arguments `ask()` sends against the signature of the real `anthropic.resources.messages.Messages.create`, so a fake cannot hide this kind of mistake again. Check: that test passes; `grep -rn temperature client.py config.py` finds nothing.
2. Add the dependencies the fetcher and the server need to `pyproject.toml` and `uv.lock`: `httpx2`, `trafilatura`, `fastapi` and `uvicorn` (tech stack, D-021, D-022). Check: `uv run python -c 'import httpx2, trafilatura, fastapi, uvicorn'` exits 0 on a fresh `uv sync`.
3. Add `client.parse()` next to `ask()`: it calls `client.messages.parse(output_format=<Pydantic model>)` and returns `response.parsed_output`. No prefill, no stop sequence, no beta header ([structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs), D-025). A `refusal` or `max_tokens` stop reason raises a clear error that the caller treats as invalid output. Check: tests with the SDK mocked (and the signature test from task 1).

**Data and reading**
4. Write `mnemo/core/store.py`: the only code that reads or writes `data/bookmarks.json`, `data/pages/<id>.txt`, `data/chat.jsonl` and `data/log.jsonl` (D-012, NF-03). Use the fields from the [data model](../../feature-specs/data-model.md), including `url_clean`, the chat message record and the log events.
5. Add URL cleaning (remove `fbclid`, `utm_*`) to make `url_clean`. Keep `url` as pasted. See [url cleaning](../../solutions/url-cleaning.md).
6. Write the fetcher in `mnemo/fetcher/`: plain pages with the limits in [page reading](../../feature-specs/page-reading.md) ("Fetch limits"), including the address checks, and GitHub repos through the official API (description and README). One retry for transient errors, then fail honestly. Pass our own bytes to `trafilatura.extract()`.
7. Add the limits to `mnemo/core/config.py` (NF-02): the maximum page length (already there) and the other fetch limits, each one as a named constant.
8. Honest failure: if the fetch fails or the text is too short, save link only, `page_status = unreadable`, `summary = null`. Never invent a summary (NF-04).
9. Write `mnemo/save/pipeline.py` and its prompt in `mnemo/save/prompts/`: system prompt, page text in XML tags, structured output through `client.parse()`. Code checks 3 to 6 tags and 60 words. Invalid output: retry once, then save link only.

**Server and API**
10. Start a small FastAPI server bound to `127.0.0.1` only (D-021, [tech stack](../tech-stack.md)). One error format.
11. `POST /api/chat`: plain code (a URL pattern) decides save, `note` or question (D-004, CI-02). A save returns a card. A message without a link gets "I can only save links for now. Asking comes later."
12. Chat history: every message is appended to `data/chat.jsonl` and `GET /api/chat/history` returns it, so the page shows the earlier messages and cards after a reload (DM-06, CI-07).
13. `PATCH /api/bookmarks/:id` with a `reason` and the `note <id> <text>` chat command (CI-02, CI-08). Sets `reason_source` to `user`. An unknown id gives 404 and "I do not have a bookmark with that number."
14. `POST /api/bookmarks/:id/open` (raises `opened_count`, writes an `open` log line), `GET /api/bookmarks` and `DELETE /api/bookmarks/:id`.

**Pages**
15. Shape the Chat page and the Bookmark page with `/impeccable` before writing HTML (D-020). The V3 mockup is the design: build to [UI reference](../../feature-specs/ui-reference.md) and the board source in `docs/design/v3-mockup/`. Its decisions are settled; keep any new layout notes in [frontend UI](../../feature-specs/frontend-ui.md). Self-host the three fonts from `mnemo/api/web/fonts/` (D-026) and check each licence file.
16. Theme and Settings: the theme control (System, Light, Dark) in the header of every screen, the Settings page on the phone, and the tokens for both themes (UI-08, UI-09, [theming](../../feature-specs/theming-and-design-tokens.md)). The choice is kept on the device.
17. Chat page: message box, card reply (title, type, 3 tags, summary, reason, bookmark number, "Filed in: Unsorted"), and a "Page not read" card with a Paste text box. No Move or Undo buttons yet: they come in phase 3. The page redraws the saved chat on load.
18. Bookmark page: list grouped by type with title, type and host, tags, date, the reason when there is one, the "guess" flag and the "page not read" badge. The title opens the link; Delete asks first. Move comes in phase 3. Every bookmark goes to Unsorted. Add the "Needs a look" banner.
19. Add the Grid and List switcher (F-05, D-015), named Cards and Ledger on the page.

**Checks**
20. Check NF-05 at 390px width: touch targets 44px, contrast 4.5:1, visible focus.
21. Parity check: compare each of the five pages with its mockup board at 1280px and 390px, light and dark, as listed in [UI reference](../../feature-specs/ui-reference.md). Put screenshots in the PR.
22. Run the 5 links. Read each summary against the page.

## Done when
- [ ] Server starts on your computer and is not reachable from another device (127.0.0.1).
- [ ] Chat box gives a card for 5 public links.
- [ ] The X post (or another unreadable page) is saved as link only; summary is null; you can paste text.
- [ ] You compared each summary with its page and found no invented fact.
- [ ] Grid and List switch on the bookmark page.
- [ ] Each page matches its mockup board, light and dark, at 1280px and 390px. Every difference is fixed or listed in the UI reference as accepted.
- [ ] A bookmark made by pasting the same link with `fbclid` is recognized as the same URL.
- [ ] After a reload, the chat page shows the earlier messages and cards.
- [ ] `note <id> <text>` changes a reason, and the row shows the user's words, not "guess".
- [ ] Opening a link raises `opened_count` and writes an `open` log line.
- [ ] `client.ask()` has no `temperature` argument, and a test checks its arguments against the real SDK signature.
- [ ] `import httpx2, trafilatura, fastapi, uvicorn` works after `uv sync`.
- [ ] `client.parse()` returns a validated object for a test schema, and a `refusal` or `max_tokens` result raises an error.
- [ ] The theme control switches System, Light and Dark, and the choice survives a reload.

## Risks
Many pages cannot be read. Structured output can still end in a refusal or a `max_tokens` cut; code treats both as invalid and retries once. See [risk review](../../research/risk-review.md).

## If time runs short
Cut the Grid view; keep List. Cut `note <id>` (edit later). Do not cut honest failure.

## Links to specs
[UI reference](../../feature-specs/ui-reference.md) · [chat and intent](../../feature-specs/chat-and-intent.md) · [page reading](../../feature-specs/page-reading.md) · [bookmark page and views](../../feature-specs/bookmark-page-and-views.md) · [frontend UI](../../feature-specs/frontend-ui.md) · [server API](../../feature-specs/server-api.md) · [storage](../../feature-specs/storage.md) · [honest failure](../../solutions/honest-failure.md) · [hard cases](../../testing/golden-sets/hard-cases.md) · [smoke checklist](../../testing/smoke-checklist.md)
