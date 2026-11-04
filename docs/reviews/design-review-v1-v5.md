# Design Review: Mockups V1 to V5
Status: Draft v0.1 · Owner: KhoiTran · Phase: 1

This file is an honest review of the five mockup versions. The mockups are in the Claude design canvas, not in this repo. Decision D-016 says the visual direction is not decided. Everything below is a review of descriptions, not of rendered pages.

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
NF-05 requires touch targets of at least 44px, text contrast of at least 4.5:1, visible focus and a working layout at 390px width. The contrast numbers in the mockup notes were estimated, not measured. Measure real contrast with a tool after you pick a direction.

## Unverified items
- Contrast numbers (estimated only).
- Rendered appearance of each mockup.
- `:has()` view switcher.
- Real `og:image` availability.

## How to decide
1. Finish phase 1 with a simple neutral style.
2. Save real links, then load them into two candidate directions.
3. Test 10 real links in each.
4. Check the save card, the "Page not read" card, and the phone list in each.
5. Pick one direction and record it in the [decision log](../process/decision-log.md) (D-016).
6. Check contrast and touch targets with real measures.

Do not build final styling before D-016 is decided. See [bookmark page spec](../feature-specs/bookmark-page-and-views.md) and [frontend UI spec](../feature-specs/frontend-ui.md).
