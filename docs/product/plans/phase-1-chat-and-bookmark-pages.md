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
1. Write `store.py`: the only code that reads or writes `data/bookmarks.json`, `data/pages/<id>.txt`, `data/chat.jsonl` and `data/log.jsonl` (D-012, NF-03). Use the record fields from the [data model](../../feature-specs/data-model.md).
2. Write the fetcher: plain pages; GitHub repos via the official GitHub API (description and README). Retry once, then fail honestly.
3. Add URL cleaning (remove `fbclid`, `utm_*`) before storing. See [url cleaning](../../solutions/url-cleaning.md).
4. Write `save.py`: system prompt, page text in XML tags, and structured output for clean JSON (D-025). Add a `client.parse()` helper next to `ask()`: it calls `client.messages.parse(output_format=<Pydantic model>)` and returns `response.parsed_output`. No prefill, no stop sequence, no beta header ([structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)). The API cannot enforce tag count or summary length, so code still checks them (3 to 6 tags, 60 words). A `refusal` or `max_tokens` stop reason is invalid output: retry once, then save link only. Do not pass `temperature`: `Messages.create()` in the installed `anthropic` 2.4.0 has no such parameter, so remove it from `ask()` too.
5. Honest failure: if fetch fails or text is too short, save link only, `page_status = unreadable`, `summary = null`. Never invent a summary (NF-04).
6. Add a max page length in `config.py` (NF-02).
7. Start a small web server bound to `127.0.0.1` only. Use FastAPI (D-021, [tech stack](../tech-stack.md)).
8. Shape the Chat page and the Bookmark page with `/impeccable` before writing HTML (D-020). Keep the agreed layout notes in [frontend-ui](../../feature-specs/frontend-ui.md). Self-host the three fonts from `web/fonts/` (D-026) and check each licence file.
9. Chat page: message box, card reply (title, type, 3 tags, summary, reason, "Filed in: Unsorted"), a "Page not read" card with a Paste text box. No Move or Undo buttons yet: they come in phase 3. Plain code (a URL pattern) decides link versus question (D-004), and `note <id> <text>` edits a reason (CI-02). The chat is saved: after a reload the page shows the earlier messages and cards (`GET /api/chat/history`, CI-07).
10. Bookmark page: list with title, reason or "guess", date, "page not read" badge, Open (sends `POST /api/bookmarks/:id/open`) and Delete (Delete asks first). Move comes in phase 3. Every bookmark goes to Unsorted; list grouped by type.
11. Add the Grid and List switcher (F-05, D-015).
12. Check NF-05 at 390px width: touch targets 44px, contrast 4.5:1, visible focus.
13. Run the 5 links. Read each summary against the page.

## Done when
- [ ] Server starts on your computer and is not reachable from another device (127.0.0.1).
- [ ] Chat box gives a card for 5 public links.
- [ ] The X post (or another unreadable page) is saved as link only; summary is null; you can paste text.
- [ ] You compared each summary with its page and found no invented fact.
- [ ] Grid and List switch on the bookmark page.
- [ ] A bookmark made by pasting the same link with `fbclid` is recognized as the same URL.
- [ ] After a reload, the chat page shows the earlier messages and cards.
- [ ] `note <id> <text>` changes a reason, and the row shows the user's words, not "guess".
- [ ] Opening a link raises `opened_count` and writes an `open` log line.

## Risks
Many pages cannot be read. Structured output can still end in a refusal or a `max_tokens` cut; code treats both as invalid and retries once. See [risk review](../../reviews/risk-review.md).

## If time runs short
Cut the Grid view; keep List. Cut `note <id>` (edit later). Do not cut honest failure.

## Links to specs
[chat and intent](../../feature-specs/chat-and-intent.md) · [page reading](../../feature-specs/page-reading.md) · [bookmark page and views](../../feature-specs/bookmark-page-and-views.md) · [frontend UI](../../feature-specs/frontend-ui.md) · [server API](../../feature-specs/server-api.md) · [storage](../../feature-specs/storage.md) · [honest failure](../../solutions/honest-failure.md) · [hard cases](../../feature-specs/test-cases/hard-cases.md) · [smoke checklist](../../manual-testing/smoke-checklist.md)
