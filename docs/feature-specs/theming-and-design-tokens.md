# Theming and Design Tokens

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, 3

This file sets how light and dark themes work and lists the colour tokens of the V3 ledger design. Decisions: D-016 (V3) and D-019 (light and dark, default System).

## Purpose

One design, two themes. The app follows the device by default. The user can force Light or Dark. Supports UI-08, UI-09 and NF-05. Screens are described in [frontend-ui.md](frontend-ui.md).

## Scope

In: theme behavior, tokens, fonts, contrast numbers, acceptance criteria.
Out: cover images, a laptop Settings screen (not designed), any other theme.

## Behavior

| Choice | Result |
| --- | --- |
| System (default) | Follows the device setting (`prefers-color-scheme`). Changes live when the device changes. |
| Light | Always light. |
| Dark | Always dark. |

- The theme control is in the header of every screen, laptop and phone.
- The phone also has a Settings tab with the same control (and the bookmark view choice). The Settings page exists at `/settings` with an Appearance group of three radio rows.
- The choice is remembered on the device. It is saved in the browser's `localStorage` under `mnemo-theme` (D-019 follow-up; no server storage). System is stored as no value.
- If saved data cannot be read, the app uses System.
- A term: a token is a named value, such as `--accent`. Components use the token name and never a raw colour.

## Tokens

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| bg | #F4F6F8 | #12151B | Page background |
| surface | #FFFFFF | #1B2029 | Cards and panels |
| ink | #101828 | #E8ECF2 | Main text |
| ink2 | #1D2939 | #CBD2DD | Second text |
| muted | #4B5565 | #A3ADBD | Notes, dates |
| line-strong | #101828 | #9AA4B5 | Strong lines |
| rule | #D0D5DD | #2D3541 | Thin dividers |
| ctl-line | #667085 | #7F8A9C | Control borders |
| accent | #C2371A | #FF8A6B | Main action, links |
| accent-hover | #8F2810 | #FFB39E | Hover state |
| on-accent | #FFFFFF | #12151B | Text on the accent |
| warn-bg | #FFF4D6 | #2A2210 | "Guess" and warning background |
| warn | #7A4B00 | #E9C46A | Warning mark |
| warn-text | #5C3800 | #F3DC9C | Warning text |

Fonts: Newsreader (serif, headings), Public Sans (body), Spline Sans Mono (labels and URLs). Self-host the font files (D-026) so the page works offline and sends nothing to Google. Serve them from `web/fonts/`, and use a fallback stack so text shows before they load. The files are in `web/fonts/` (variable woff2: `Newsreader.woff2`, `PublicSans.woff2`, `SplineSansMono.woff2`), converted from the google/fonts GitHub repo (`ofl/` folders), each with its `*-OFL.txt` next to it. Licence status: the OFL text was fetched from the same repo; it was not compared line by line with the upstream project licence (**Unverified**).

## Contrast (measured on the mockup colours)

Ratio of text colour to background colour. The goal is 4.5:1 for text (NF-05) and 3:1 for control borders.

| Pair | Light | Dark |
| --- | --- | --- |
| ink on bg | 16.38 | 15.42 |
| ink2 on bg | 13.57 | 12.01 |
| muted on bg | 6.96 | 8.07 |
| accent on bg | 5.03 | 7.92 |
| on-accent on accent | 5.45 | 7.92 |
| warn on warn-bg | 6.76 | 9.42 |
| warn-text on warn-bg | 9.48 | 11.63 |
| ink on surface | 17.75 | 13.78 |
| muted on surface | 7.54 | not measured |
| accent on surface | 5.45 | not measured |
| ctl-line on bg | 4.59 | 5.24 |
| ctl-line on surface | not measured | 4.68 |
| line-strong on bg | 16.38 | 7.27 |
| rule on bg (decoration only) | 1.36 | 1.48 |

Notes:
- `rule` is only a thin divider. It is below 3:1 on purpose. Never use it as the only sign of a control.
- These numbers are from the mockup. They are **unverified** in the built page. Measure again after phase 1.
- Not measured: hover, focus ring, disabled state, text on a photo.

## Acceptance criteria

1. With the device in light mode and the app on System, the app is light. In dark mode it is dark. No restart.
2. Choosing Light or Dark overrides the device. Choosing System returns to following it.
3. After a reload, the choice is still applied.
4. No text is below 4.5:1 in either theme, measured in the built page.
5. No colour value appears in a component rule. Only token names.
6. No flash of the wrong theme on load (unverified; test on the iPhone).
7. Focus is visible in both themes (UI-04).

## Notes for the build

- Define every token once for light, then redefine for dark under the system media query and under an explicit dark setting. The explicit setting must win over the device setting.
- Tokens live in `web/css/tokens.css` (the only file with raw colours). Dark is written twice: under `prefers-color-scheme` guarded by `:root:not([data-theme="light"])`, and under `:root[data-theme="dark"]`. `web/js/theme.js` runs in `<head>` before first paint. No flash and storage-unreadable fallback are **Unverified** in a real browser.
- Set `color-scheme` so form controls and scrollbars follow the theme.
- The mockup used the CSS `:has()` selector for the theme control. Plain code with a data attribute on the root element is simpler. `:has()` is unverified in the viewer.

## Open questions

- A laptop Settings screen, or keep the header control only.
- Whether the accent needs a second colour for success and error states.
- Font licences: confirm each `*-OFL.txt` against the upstream project (Q-16 itself is answered: self-host).

Related: [frontend UI](frontend-ui.md), [bookmark page](bookmark-page-and-views.md), [decision log](../process/decision-log.md), [design review](../reviews/design-review-v1-v5.md).
