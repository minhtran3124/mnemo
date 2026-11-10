# UI reference (V3 mockup parity)

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, 3

This file says how the built pages must follow the V3 mockup, and lists where they may differ. Decisions: D-016 (V3 ledger), D-019 (light and dark), D-026 (self-hosted fonts).

## Source of truth

- The mockup is the canvas "Bookmark Brain Mockup" on claude.ai (private). Its five final boards are saved as source in [docs/design/v3-mockup/](../design/v3-mockup/README.md). Read those files for exact sizes, spacing and wording.
- **Look:** the mockup wins. Sizes, spacing, type, borders, wording of the cards, and where each control sits follow the board.
- **Behaviour and scope:** the specs and the phase plan win. A board shows the finished app; a phase builds part of it.
- Colours come only from tokens ([theming](theming-and-design-tokens.md), UI-09). The token table already matches the boards (checked against the `.th` block of the light boards on 2026-11-05).
- Any difference not listed below is a bug in the build, not a design choice.

## Screens

| Screen | Board | In phase 1 |
| --- | --- | --- |
| Chat, laptop | `V3LightChat` | Built at `/` (web/index.html), without the parts listed under "Not built yet". Compared with the board in a browser on 2026-11-05 at 1280px, light and dark; the differences left are under "Accepted differences" |
| Bookmark page, laptop | `V3LightBookmarks` | Yes, Ledger and Cards views. Both compared with the board in a browser on 2026-11-05 |
| Chat, phone | `V3LightPhoneChat` | Built with the same page (margin column becomes a "Filed in" line under the text). Compared at 390px, light and dark, on 2026-11-05. NF-05 measured at 390px, light: pass ([check](../testing/phase1-nf05-check.md)) |
| Bookmarks, phone | `V3LightPhoneList` | Yes |
| Settings, phone | `V3LightSettings` | Theme is built; the bookmark view choice and the preview are not (A10). At 1280px there is no board: compared with the phone board and the measurement tables |
| Dark versions of all five | `V3Dark*` | Yes. Same markup as the light board; only the token set differs (see the [README](../design/v3-mockup/README.md)) |

## Accepted differences

Result of the parity check of 2026-11-05 (see [phase 1 parity check](../testing/phase1-parity-check.md); screenshots are in the PR). The Ledger and Cards views were both compared with the boards in screenshots and computed styles, at 1280px and 390px, light and dark. The Cards box, grid and gaps match the boards; the one size difference found (row title and meta on the phone) was fixed. Each line is a difference the build keeps for now.

- A1 **All pages, header.** The board has Chat and Bookmarks tabs with a count (laptop) and a bottom tab bar (phone). The build has the brand, a Settings link and the theme control. Reason: the tabs are not built (see the Open question under "Chat page as built"); the count needs server data.
- A2 **Chat, both widths.** No Move and Undo buttons and no real folder name: phase 3.
- A3 **Chat, both widths.** No "Try asking" chips, no helper line, no "Found in" answer entry, and the composer placeholder is the phase 1 text: phase 4.
- A4 **Chat, both widths.** Extra "No. N" in the margin, a URL line and a plain reply line under a card: documented additions (CI-08, "Page not read" entry, partial failure text).
- A5 **Chat, both widths.** The folder and type icons are missing in the card, and the "Page not read" paragraph is the generic text, not the X post text of the board. The card is built in `mnemo/api/web/js/chat.js`, which was outside ticket 42.
- A6 **Bookmarks, both widths.** The title is "Bookmarks", with no count sentence, no search box, no "Show all N" link, and a shorter banner without a "Paste its text" button. Search comes in phase 4 and 5. The rest is built in `mnemo/api/server.py`, which was outside ticket 42.
- A7 **Bookmarks, both widths.** Groups are types, not folders: phase 3.
- A8 **Bookmarks, both widths.** The meta line shows the type name, host and save date in plain text, with no type icon and no "Article on host" wording; a summary, a reason and a Delete button sit in the row. The save date, reason and Delete are documented additions (BP-04, decisions 1 and 2). The icon and wording come from `mnemo/api/server.py`, outside ticket 42.
- A9 **Bookmarks, both widths.** The view switcher has Ledger and Cards, no Compact: phase 3.
- A10 **Settings, both widths.** The "Bookmark view" section, its Compact row and the preview entry are not built. They need a script change outside ticket 42 (the choice is stored by `view-switcher.js`).
- A11 **Settings, 1280px.** No board exists. The page keeps the phone layout in a narrow column; compared with the phone board and the measurement tables.
- A12 **Bookmarks, 390px.** Delete sits under the row text on the phone; the board has no Delete (decision 1).
- A13 **Each board at the other width.** A board is drawn at one width only (laptop boards at 1280px, phone boards at 390px). The build shows each page at both widths, so the other width was read against the laptop or phone column of the measurement table, not against a board.
- A14 **Bookmarks, Cards view.** The card contents differ as in A8 and A12 (summary, reason and Delete inside the card, tags on their own line). At 1280px the board draws the content column 40px further in than the header, so its three cards are 352px wide; the build keeps the 48px page padding, so they are 379px wide. Border, radius, fill, padding, gap, columns and the title and meta sizes match at both widths.

## Measurements from the boards

| Item | Laptop | Phone |
| --- | --- | --- |
| Body text | 17px, line height 1.55 | 16px, line height 1.5 |
| Page padding | 48px sides | 16px sides |
| Chat column | max 860px, centred | full width |
| Bookmark page column | max 1184px, centred | full width |
| Wordmark "Mnemo" | Newsreader 700, 28px | 24px |
| Rule under the header | 3px double `line-strong` | same |
| Page title (h1) | Newsreader 700, 48px, tight (-0.02em) | 32px |
| Folder or group heading (h2) | Newsreader 600, 30px, count in Spline Sans Mono 14px `muted` | 24px, count 13px |
| Chat entry title | Newsreader 600, 32px | 26px |
| List row title | Newsreader 600, 21px | 19px |
| Row meta line | 14px `muted`; tags in Spline Sans Mono 12px | 13px |
| URL the user pasted | Spline Sans Mono 13px in a bordered box, right-aligned, max 80% | 12px, max 92% |
| Buttons | min height 44px, radius 6px, 1px `line-strong` border, `surface` fill, 15px weight 600 | same |
| Primary button | `accent` fill, `on-accent` text (Save, Paste the text) | same |
| Inputs | min height 48px, radius 6px, 1px `line-strong` border | same |
| Focus | 2px `ink` outline, 2px offset; 3px `accent` on the theme control | same |
| Motion | none; honour `prefers-reduced-motion` | same |

Fonts and weights to self-host: Newsreader 500, 600, 700 (optical size 6 to 72), Public Sans 400 to 700, Spline Sans Mono 400 and 500. Icons are inline stroke SVG (24px grid, stroke 1.75), never emoji and never an icon font.

## Parts and their rules

- **Header:** wordmark left; on the laptop the nav (Chat, Bookmarks with a count in mono) in the middle and the theme control on the right. On the phone the nav is a bottom bar with three tabs: Chat, Bookmarks with count, Settings. The active tab is bold, underlined 2px, offset 8px.
- **Theme control:** three 44px buttons in one bordered group: System, Light, Dark (monitor, sun, moon icons). The checked one is filled with `ink`. It is in the header of every screen, on the phone too, and also in Settings.
- **Chat entry (a saved link):** a margin column 150px wide with "Filed in" and the folder name with a folder icon; the main column has the type line with icon ("Article on claude.dev"), the title, the summary, the tags in mono, then "Why you saved it:" with the reason and a "guess" flag when Claude wrote it. A 1px `line-strong` rule sits above each entry. On the phone the margin column becomes a "Filed in" line under the text.
- **Page not read entry:** a warning label (`warn-bg`, `warn` border, triangle icon) saying "Page not read", a title, one paragraph, then the primary button "Paste the text".
- **Composer:** fixed at the bottom with a 1px `rule` above it; one bordered box holding the text field and the primary "Save" button (48px high on the laptop). A helper line below on the laptop only.
- **Bookmark row:** title, then a meta line: type icon, "Article on claude.dev", tags in mono, and a bordered `warn` flag "reason is a guess" (phone: "guess"). Rows are separated by 1px `rule`. On the laptop rows wrap into two columns (min 440px, 40px gap). A whole row is a link.
- **Group section:** a 1px `line-strong` rule, the heading with its count, and "Show all N" at the right when the group is cut.
- **"Needs a look" banner:** a bordered `warn` box on the bookmark page: "One link could not be read. It is in Unsorted…", with a "Paste its text" button on the laptop.
- **View switcher:** a bordered group with Ledger, Cards, Compact (Ledger is the default). On the phone it is full width.
- **Settings (phone):** a title, "Appearance" with three radio rows (System is the default), a preview entry, then "Bookmark view" with three radio rows and the line "Mnemo remembers your choice on this device."

## The three views (from the bookmark boards)

| View | Laptop | Phone |
| --- | --- | --- |
| Ledger (default) | Rows without boxes, 1px `rule` between them, two columns (min 440px, 40px gap) | One column, row padding 12px |
| Cards | Boxed tiles: 1px `line-strong` border, 6px radius, `surface` fill, padding 14px 16px. Three equal columns, 16px gap | One column, 10px gap |
| Compact | Two equal columns, 40px gap. Each item is one line: title 16px, meta 13px on the same line, tags hidden, min height 44px | One column |

The switcher is one bordered group with a 4px inner gap. Each option is 44px high with an icon and a label (list, grid and rows icons). The selected option is filled with `ink` and its text uses `on-accent`. On the phone the three options share the full width.

## Not built yet in phase 1 (hide it, do not show a dead control)

| Part on the board | Comes in |
| --- | --- |
| Move and Undo buttons, and a real folder name in "Filed in" | Phase 3. Until then the margin shows "Unsorted" |
| Compact in the view switcher and Settings | Phase 3 |
| "Found in" answer entry and the "Try asking" chips | Phase 4 |
| The helper line "You can also paste text from Slack" | Phase 4 (import) |
| Folder headings with real folders | Phase 3. In phase 1 the groups are the types |
| Composer placeholder "…or ask about your bookmarks" | Phase 4. In phase 1: "Paste a link to save it" |

## Chat page as built (phase 1)

- The page shows no nav counts, no "Try asking" chips and no helper line. The shared header has only the brand, Settings and the theme control; the Chat and Bookmarks tabs of the board are not built yet (**Open question**: the header partial is outside this ticket).
- A card has the margin column (Filed in, folder or "Unsorted", "No. N"), the type line, title, summary, up to 3 tags and "Why you saved it:" with a "guess" flag. The live reply and the redrawn history use the same card builder.
- A saved bookmark whose page was not read gets the "Page not read" card with a "Paste the text" box. Save sends `POST /api/bookmarks/{id}/paste` with `{"text": "..."}` and replaces the card with the returned record. Errors show a short line by code: `text_too_short`, `summary_failed`, `already_read`; anything else shows "Something went wrong. Try again." The route is built in ticket #62 (see its docs in `server-api.md` and `honest-failure.md`); the page follows that contract and is **Unverified** against the real route until #62 merges.
- A link that was not saved (`failed`) shows "I could not save this link." with no Paste box, because it has no bookmark id.
- The saved chat is redrawn from `GET /api/chat/history`; a deleted bookmark shows "Bookmark N was deleted."
- Reply cards were checked in a browser at 1280px and 390px, light and dark, on 2026-11-05 (see Accepted differences).

## Wording that comes from the board

The cards use the board's text, not the first draft in the specs:

| Case | Text |
| --- | --- |
| Page not read, title | "I could not read this page. I saved the link only." |
| Page not read, X post | "The site does not let me open it, so I have no summary. I will not guess what is on it. Paste the text of the post and I will make the entry." |
| Slack link, title | "I cannot open Slack links. I saved the link only." |
| Slack link, body | "Copy the message in Slack and paste it here. I will find the links in it." |
| Banner | "One link could not be read. It is in Unsorted." |

For another unreadable page, keep the title and use one honest line for the cause that the app knows (for example a timeout). Never guess a cause.

## Additions that the board does not show

These come from the specs and need a place in the layout. Put them where the ledger style suggests (decisions 1 and 2 below fix two of them), and show the result in the parity check.

| Addition | Where | Why |
| --- | --- | --- |
| Bookmark number ("No. 42", mono, `muted`) | Under the folder in the entry's margin column | `note <id>` needs it (CI-08) |
| Save date | In the row meta line | BP-04. The board leaves dates out |
| Open and Delete | Decisions 1 | BP-05 |
| Delete confirmation | A dialog or inline confirm, 44px buttons | BP-08 |
| Empty and error states | Plain text, same type scale | UI acceptance 5 |

## Decisions (settled 2026-11-05)

1. **Row actions.** The title of a row opens the link (`url_clean`, in a new tab) and sends `POST /api/bookmarks/:id/open` in the background. A text button "Delete" (44px high) sits at the right of the meta line and asks for confirmation (BP-08). Move joins it in phase 3.
2. **Reason on a row.** When a reason exists, show it under the meta line. The "reason is a guess" flag stays beside the meta when Claude wrote it.
3. **A question in phase 1.** Asking is built in phase 4. In phase 1 a message without a link (and not `note <id> <text>`) gets this app message: "I can only save links for now. Asking comes later." Nothing is searched and nothing is sent to Claude.
4. **Type names on the page.** `github_repo` "Code repository", `article` "Article", `docs` "Documentation" (if D-013 is accepted), `pdf` "PDF book", `video_page` "Video", `tool` "Tool", `image` "Image", `note` "Note", `other` "Page". The first four are in the board; the rest are new and can change when `/impeccable` shapes the pages.
5. **View columns.** Follow the boards, not the one-line texts in Settings: Ledger rows wrap into two columns on the laptop (from about 960px); Cards are three columns on the laptop; the phone has one column in every view.

## Parity check (part of the phase 1 done-when)

1. For each of the five screens, open the built page next to the board source at 1280px and 390px, in light and in dark.
2. Compare type sizes, spacing, borders, wording and control positions with the tables above. Use `/impeccable critique` on the built page.
3. Search the CSS for raw colour values and font stacks: only tokens may appear (UI-09).
4. Put screenshots in the PR. List each difference as "fixed" or add it to this file as accepted, with the reason.
5. Measure contrast and touch targets in the built page (NF-05); the numbers in the theming spec come from the mockup and are unverified.

Related: [frontend UI](frontend-ui.md), [theming and tokens](theming-and-design-tokens.md), [bookmark page and views](bookmark-page-and-views.md), [chat and intent](chat-and-intent.md), [design review](../research/design-review-v1-v5.md), `PRODUCT.md`.
