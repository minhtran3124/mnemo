# Frontend UI

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, 3, A

This file lists the screens, the responsive rules and the quality bar for the web pages.

## Purpose

The screens are thin: the server holds the key and the data (D-002). This spec sets what the screens must do and how good they must be. Supports F-04 and NF-05.

## Scope

In: screens, responsive rules, components, cover images, empty and error states, design direction status.
Out: the final visual style, which is not decided.

## Requirements

| ID | Requirement |
| --- | --- |
| UI-01 | Two screens: Chat ([chat-and-intent.md](chat-and-intent.md)) and Bookmark page ([bookmark-page-and-views.md](bookmark-page-and-views.md)). |
| UI-02 | Touch targets are at least 44px (NF-05). |
| UI-03 | Text contrast is at least 4.5:1 (NF-05). |
| UI-04 | Focus is always visible (NF-05). |
| UI-05 | The pages work at 390px width with no sideways scroll (NF-05). |
| UI-06 | The same pages work on a laptop and on an iPhone browser. |
| UI-07 | The page never holds the API key. |

## Components

Message box, card, "Page not read" card with Paste text field, Move menu, Undo button, folder list with counts, filter controls, search box, view switcher, row, badge, import page, empty and error states.

## Design direction

Decision D-016: the visual direction is not decided. Five mockups exist (V1 to V5):

| Mockup | Idea |
| --- | --- |
| V1 | Light paper, bold outlines, cobalt and yellow, 4px shadows |
| V2 | Dark, calm, three panes for scanning |
| V3 | Ledger, serif, folder in the margin, "guess" labels |
| V4 | Covers first, cream and forest green and yellow, serif display |
| V5 | Soft glass, capsule covers, one blue action |

You said earlier versions felt like "AI slop". The cause is not found yet. See [design-review-v1-v5.md](../reviews/design-review-v1-v5.md). Do not build a final style until a direction is chosen.

## Cover images (proposed)

Covers in the mockups are drawn stand-ins. The real app should use the page's own preview image (`og:image`, the picture a site names for sharing) when it exists. If it does not exist, draw a fallback. Open question: draw it from type and title, or use a plain icon.

## Empty states

| Where | Text idea |
| --- | --- |
| Chat, no saves | Tell the user to paste a link. |
| Bookmark page, no bookmarks | Point to the chat and to import. |
| Search, no result | "nothing found" |

Final wording: Open question.

## Error states

| Error | What the user sees |
| --- | --- |
| Page not readable | "Page not read" card, paste option |
| Server not reachable | A clear message, no blank page |
| API error or limit reached | A short message; the bookmark is still saved as link only. Open question: exact behavior |
| Login failed (phase A) | A short message |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | At 390px width, nothing scrolls sideways. |
| 2 | All buttons are at least 44px high and wide. |
| 3 | A contrast tool shows at least 4.5:1 for body text. |
| 4 | Tab key reaches every control and shows focus. |
| 5 | Each empty and error state has text, not a blank area. |

## Tests

Manual: see `manual-testing`.

## Open questions

- Design direction (D-016).
- Cover fallback style.
- Wording of empty and error states.
