# Design Review: Mockups V1 to V5
Status: Draft v0.1 · Owner: KhoiTran · Phase: 1

This file is an honest review of the five mockup versions. The mockups are in the Claude design canvas, not in this repo. Decision D-016 (Accepted) chose V3, with light and dark themes (D-019). This file keeps the review as history and lists what is still unverified. Everything below is a review of descriptions, not of rendered pages.

Mockup: https://claude.ai/artifact/7Q93Na93mLjP5FCbWbeYwz

All five versions show a laptop chat, a laptop bookmark page, a phone chat and a phone list.

## The five versions

| Version | What it tries | Strengths | Weaknesses |
| --- | --- | --- | --- |
| V1 | Light paper, bold outlines (cobalt and yellow, 4px shadows) | Strong, clear shapes; easy to tell buttons from text | Text-only list; heavy outlines may tire the eye in a long list |
| V2 | Dark, calm, three-pane for scanning | Good for scanning many rows | Three panes are hard to fit on a phone; dark mode contrast needs checking |
| V3 | Ledger look, serif, folder in the margin, "guess" labels | Shows the "guess" label clearly, which supports NF-04 | Dense; all text; small type may fail the touch and reading rules |
| V4 | Covers first, cream, forest green and yellow, serif display | Has a visual hook (covers) | Covers are drawn stand-ins, not real page images |
| V5 | Soft glass, capsule covers, one blue action (inspired by a pastel chat app) | One clear action; soft look | Glass effects can lower contrast; covers are stand-ins |

## Why it felt like "AI slop"
You said earlier versions felt like "AI slop". The cause is unresolved. These five reasons are my best reading.

1. The same skeleton is used in every version. Only colors and fonts change.
2. V1 to V3 are all text. There is nothing to look at.
3. No memorable main moment. The save card is where the user feels the product, and no version makes it special.
4. No version was checked as a rendered page. Layout problems would show only when rendered.
5. The sample content is plain. Invented titles do not show how real links look.

## Covers
V4 and V5 use covers. A cover is a picture for each bookmark. In the real app, use the page's own preview image (`og:image`) when it exists and draw a fallback otherwise (proposed). Unverified: how often real pages have an `og:image`. Test this with the sample links.

## View switcher
The bookmark page has Grid, List and Compact views (D-015, F-05). Unverified: the `:has()` CSS approach for the switcher in the viewer. Test it in your browser before relying on it.

## Accessibility notes
NF-05 requires touch targets of at least 44px, text contrast of at least 4.5:1, visible focus and a working layout at 390px width. The contrast numbers in the mockup notes were estimated, not measured. Contrast for V3 was later measured on the mockup colours (see the theming spec). Measure again in the built page.

## Unverified items
- Contrast numbers (V3 measured on mockup colours only).
- Rendered appearance of each mockup.
- `:has()` view switcher.
- Real `og:image` availability.

## Decision recorded
- D-016: V3, the ledger.
- D-019: light and dark, default follows the system setting.
- V3 weak points listed above still apply: it is dense and all text.
- Tokens and rules: [theming-and-design-tokens.md](../feature-specs/theming-and-design-tokens.md).

## What is still to verify
1. Render the mockup in a real browser and check both themes.
2. Check the save card, the "Page not read" card and the phone list with 10 real links.
3. Check that V3 small type still passes the touch and reading rules (NF-05).
4. Measure contrast again in the built page. The numbers in the theming spec come from the mockup colours.
5. Check the `:has()` switcher and the System theme in Safari on the iPhone.

See [bookmark page spec](../feature-specs/bookmark-page-and-views.md) and [frontend UI spec](../feature-specs/frontend-ui.md).
