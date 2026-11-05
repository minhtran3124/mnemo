# Bookmark page and views (Screen 2)

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, 3

This file describes the bookmark page and its three views: Grid, List and Compact.

## Purpose

The bookmark page shows everything you saved. It supports F-04 and F-05, and decision D-015 (a Grid/List/Compact switcher).

## Scope

In: folders panel, filters, search, row fields, badges, actions, the three views.
Out: visual style (see [frontend-ui.md](frontend-ui.md)); how search works (see [search-no-embeddings.md](search-no-embeddings.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| BP-01 | The left side shows folders with counts. |
| BP-02 | The main area shows bookmarks of the selected folder. |
| BP-03 | You can filter by type and by tag, and you can search. |
| BP-04 | Each row shows: title, type and host, tags, date, the reason when there is one, a "reason is a guess" flag when Claude wrote it, and a "page not read" badge when `page_status` is `unreadable`. |
| BP-05 | The title of a row opens the link and logs the open. Each row has a Delete button that asks first. From phase 3 it also has Move. |
| BP-06 | A view switcher offers Grid, List and Compact. |
| BP-07 | Opening a link raises `opened_count` and writes a log line. |
| BP-08 | Delete asks for confirmation. Nothing is deleted without your action (product rule 3). |

## Behavior and rules

| View | Shows | Ships |
| --- | --- | --- |
| Grid | Cover image, title, type, reason or "guess" | Phase 1 |
| List | One row per bookmark: title, reason or "guess", date, badge, actions | Phase 1 |
| Compact | Dense rows: title and the most useful fields only | Phase 3 |

- Default view: List. In the V3 design it is called Ledger, and Grid is called Cards (D-016).
- Remembered choice (proposed): the page remembers the last view.
- In phase 1, folders are not real yet: every bookmark is in `Unsorted` and the list is grouped by type. Real folders come in phase 3.
- A reason marked "guess" is labeled so you can tell your words from the app's.
- Cover images follow the rule in [frontend-ui.md](frontend-ui.md).

### Built in phase 1 (list view)

- Served at `GET /bookmarks`. The server draws the list, grouped by type in a fixed order (empty groups skipped). All bookmarks are in Unsorted.
- Each row shows title, type, host, date, tags, the reason (with a "guess" flag only when `reason_source` is `guess`), and a "page not read" badge for unreadable pages (no summary shown).
- Test hooks in the markup: `data-open-url` on the title link, `data-delete-url` and `data-confirm` on the Delete button. There is no Move button before phase 3.
- A "Needs a look" banner shows only when at least one unreadable bookmark exists. After a delete, the page script removes the banner when the last unreadable row is gone, and shows the empty message when the last bookmark is gone.
- Not built here: the Grid/List switcher, folders panel, filters and search.
- **Unverified**: the click flow (open logs a count, Delete confirm and row removal, error message) and the 390px layout have not been checked in a real browser.

### Mockups

Five mockups (V1 to V5) exist in the Claude design canvas. They are not in this repo. They are mockups only. A view switcher built with the CSS `:has()` selector was used in a mockup. Unverified: that `:has()` works in the real viewer. Test it in the real browser.

## Edge cases

| Case | Behavior |
| --- | --- |
| No bookmarks | Empty state (see [frontend-ui.md](frontend-ui.md)). |
| Unreadable page | Badge "page not read"; no summary shown. |
| No cover image | Drawn fallback (proposed). |
| Very long title | Cut with an ellipsis; full title on open. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | Folder counts equal the number of rows in each folder. |
| 2 | Filter by type and tag returns only matching rows. |
| 3 | Each unreadable bookmark shows the badge. |
| 4 | Grid and List switch without a page reload problem, at 390px width too. |
| 5 | Delete needs a confirmation. |

## Tests

Manual smoke test in `manual-testing`. Data from [data-model.md](data-model.md).

## Open questions

- Which fields Compact shows.
- Whether the view choice is remembered, and where.
