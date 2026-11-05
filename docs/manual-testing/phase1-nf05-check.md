# Phase 1 NF-05 check at 390px

Touch targets, text contrast and visible focus on the five phone screens (UI-reference, light theme).

| Screen | Check | Result | Measured |
| --- | --- | --- | --- |
| Chat (`/`) | Touch targets | pass | 8 controls, smallest 69 x 44px (wordmark link, after the fix) |
| Chat (`/`) | Text contrast | pass | 38 text pairs, lowest 4.61:1 (composer placeholder) |
| Chat (`/`) | Focus | pass | 8 Tab stops, all with an outline: 3px `accent` on header controls (5.45:1), 2px on buttons and composer (at least 16.38:1) |
| Bookmarks, Ledger (`/bookmarks`) | Touch targets | pass | 15 controls, smallest 64.7 x 44px (a one-word title link) |
| Bookmarks, Ledger (`/bookmarks`) | Text contrast | pass | 55 text pairs, lowest 5.03:1 (row title link) |
| Bookmarks, Ledger (`/bookmarks`) | Focus | pass | 15 Tab stops, all 3px `accent` outline, lowest 5.03:1 |
| Bookmarks, Cards (`/bookmarks`) | Touch targets | pass | 15 controls, smallest 64.7 x 44px |
| Bookmarks, Cards (`/bookmarks`) | Text contrast | pass | 55 text pairs, lowest 5.03:1 |
| Bookmarks, Cards (`/bookmarks`) | Focus | pass | 15 Tab stops, all 3px `accent` outline, lowest 5.03:1 |
| Settings (`/settings`) | Touch targets | pass | 8 controls, smallest 69 x 44px; radio rows 324 x 44px |
| Settings (`/settings`) | Text contrast | pass | 11 text pairs, lowest 5.45:1 |
| Settings (`/settings`) | Focus | pass | 6 Tab stops, all 3px `accent` outline, 5.45:1 |
| Page not read (chat card, paste box open) | Touch targets | pass | 10 controls, smallest 68.4 x 44px (paste Save); paste field 358 x 174.8px |
| Page not read (chat card, paste box open) | Text contrast | pass | 40 text pairs, lowest 4.61:1 |
| Page not read (chat card, paste box open) | Focus | pass | 9 Tab stops, 3px `accent` on the header, 2px outline on the card and composer buttons and fields (at least 16.38:1) |

## Notes

- Method: `uv run` server from the worktree on port 8741 with seeded `data/` (4 bookmarks: 2 articles, 1 repo, 1 video; one is unreadable, with a guessed reason on one; a 4-message chat). Headless Chrome through Playwright, viewport 390 x 844, mobile and touch emulation, light colour scheme, `mnemo-theme` set to `light`. No horizontal scroll on any screen (scroll width 390).
- Touch: every visible `a`, `button`, `input`, `textarea` and radio label was measured with `getBoundingClientRect`; the limit is 44px high and wide.
- Contrast: every visible text node, plus the composer placeholder, against the real background (alpha blended up the ancestors). The limit is 4.5:1 for all text, including large text.
- Focus: Tab through the page in order; for each stop the computed outline style, width and colour were read, and the outline colour was compared with the background behind it (the limit is 2px wide and 3:1). On the Page-not-read screen, Enter on "Paste the text" opened the box during the Tab pass.
- Fix made: the "Mnemo" wordmark link was 69 x 31px on all screens. It now has `min-height: var(--control)` in `web/css/base.css`. All three checks were run again after the fix.
- Five screens: Chat, Bookmarks (Ledger), Bookmarks (Cards), Settings, and the Page-not-read state. Ledger and Cards are both rows of "Bookmarks, phone".
- Focus colour: the build uses a 3px `accent` outline on the header and list controls; ui-reference says 2px `ink`. This is a parity item, not an NF-05 failure.
- Not measured: widths other than 390px, the dark theme, and a real screen reader (parity ticket and later). Contrast of control borders and icons was not measured.
