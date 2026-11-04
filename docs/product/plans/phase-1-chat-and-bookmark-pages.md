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
Phase 0 done. A list of 5 public links to test (see [sample links](../../reference/sample-links.md)), including one unreadable page such as an X post.

## Tasks
1. Write `store.py`: the only code that reads or writes `data/bookmarks.json`, `data/pages/<id>.txt` and `data/log.jsonl` (D-012, NF-03). Use the record fields from the [data model](../../feature-specs/data-model.md).
2. Write the fetcher: plain pages; GitHub repos via the official GitHub API (description and README). Retry once, then fail honestly.
3. Add URL cleaning (remove `fbclid`, `utm_*`) before storing. See [url cleaning](../../solutions/url-cleaning.md).
4. Write `save.py`: system prompt, low temperature, page text in XML tags, prefill plus stop sequence for clean JSON. Test prefill first; if the model rejects it, ask for JSON in tags and parse in code (Unverified).
5. Honest failure: if fetch fails or text is too short, save link only, `page_status = unreadable`, `summary = null`. Never invent a summary (NF-04).
6. Add a max page length in `config.py` (NF-02).
7. Start a small web server bound to `127.0.0.1` only. Use FastAPI (D-021, [tech stack](../tech-stack.md)).
8. Chat page: message box, card reply (title, type, 3 tags, summary, reason), a "Page not read" card with a Paste text box. Plain code (a URL pattern) decides link versus question (D-004).
9. Bookmark page: list with title, reason or "guess", date, "page not read" badge, Open/Move/Delete. Every bookmark goes to Unsorted; list grouped by type.
10. Add the Grid and List switcher (F-05, D-015). Add `note <id>` to edit a reason.
11. Check NF-05 at 390px width: touch targets 44px, contrast 4.5:1, visible focus.
12. Run the 5 links. Read each summary against the page.

## Done when
- [ ] Server starts on your computer and is not reachable from another device (127.0.0.1).
- [ ] Chat box gives a card for 5 public links.
- [ ] The X post (or another unreadable page) is saved as link only; summary is null; you can paste text.
- [ ] You compared each summary with its page and found no invented fact.
- [ ] Grid and List switch on the bookmark page.
- [ ] A bookmark made by pasting the same link with `fbclid` is recognized as the same URL.

## Risks
Many pages cannot be read. Prefill may fail on some models. See [risk review](../../reviews/risk-review.md).

## If time runs short
Cut the Grid view; keep List. Cut `note` (edit later). Do not cut honest failure.

## Links to specs
[chat and intent](../../feature-specs/chat-and-intent.md) · [page reading](../../feature-specs/page-reading.md) · [bookmark page and views](../../feature-specs/bookmark-page-and-views.md) · [frontend UI](../../feature-specs/frontend-ui.md) · [server API](../../feature-specs/server-api.md) · [storage](../../feature-specs/storage.md) · [honest failure](../../solutions/honest-failure.md) · [hard cases](../../feature-specs/test-cases/hard-cases.md) · [smoke checklist](../../manual-testing/smoke-checklist.md)
