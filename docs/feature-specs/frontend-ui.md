# Frontend UI

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, 3, A

This file lists the screens, the responsive rules and the quality bar for the web pages.

## Purpose

The screens are thin: the server holds the key and the data (D-002). This spec sets what the screens must do and how good they must be. Supports F-04 and NF-05.

## Scope

In: screens, responsive rules, components, cover images, empty and error states, design direction status.
Out: a laptop Settings screen (only the phone Settings screen is designed). Cover images are not in V3.

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
| UI-08 | Light, Dark and System themes. System is the default and follows the device (D-019). |
| UI-09 | Every colour comes from a token. No colour is written inside a component rule ([theming-and-design-tokens.md](theming-and-design-tokens.md)). |

## Components

Message box, card, "Page not read" card with Paste text field, Move menu, Undo button, folder list with counts, filter controls, search box, view switcher, row, badge, import page, empty and error states.

## Design direction

Decision D-016 (Accepted): the visual direction is **V3, the ledger**. Serif headings, the folder in the margin, "guess" labels. Decision D-019 (Accepted): the app has a light theme and a dark theme. The default follows the system setting. Tokens and rules are in [theming-and-design-tokens.md](theming-and-design-tokens.md).

Mockup (light and dark, laptop and phone, Settings screen): https://claude.ai/artifact/7Q93Na93mLjP5FCbWbeYwz
The mockup was never checked as a rendered page and the link is not a permanent store. The tokens in the spec are the source of truth.

V1, V2, V4 and V5 are dropped. They stay in the mockup file and in the [design review](../reviews/design-review-v1-v5.md) as history.

| Item | Decision |
| --- | --- |
| Look | V3 ledger. Fonts: Newsreader (serif), Public Sans, Spline Sans Mono |
| Theme | System (default), Light, Dark |
| Theme control | Laptop: in the header. Phone: in Settings |
| Remembered | The choice is saved on the device. Where exactly is an open question |
| Default bookmark view | Ledger (the V3 list). Grid is shown as Cards |
| Covers | Not in V3. See below |

## Cover images (proposed)

Covers in the mockups are drawn stand-ins. The real app should use the page's own preview image (`og:image`, the picture a site names for sharing) when it exists. If it does not exist, draw a fallback. V3 has no covers, so this is not needed in phase 1. Open question: add covers later, or keep the ledger text-only.

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

- Laptop Settings screen: not designed. Does the theme control stay in the header?
- Where the theme choice is saved (browser storage or server).
- Cover fallback style.
- Wording of empty and error states.
