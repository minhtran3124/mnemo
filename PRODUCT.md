# Product

<!-- impeccable:product-schema 1 -->

> Source: written by `/impeccable init` from the docs in `docs/` (PRD, decision log, frontend and theming specs). No interview was held, because the owner asked for a fully automatic run. Facts marked **(inferred)** come from the docs and have not been confirmed in person. Confirm or correct them at the next UI session.

## Platform

web

## Stack

Python with FastAPI, serving plain HTML, CSS and JS pages with no build step, bound to `127.0.0.1` (D-021). Full list in [tech stack](docs/product/tech-stack.md). Whatever is chosen must keep the page thin: no API key in the page (UI-07, D-002).

## Users

One person: the owner. Public links only while building (D-018). The same pages must work on a laptop and in an iPhone browser (UI-06). The user saves links in seconds, then later asks for them in their own words. **(inferred)** Reading and writing are in English (D-011).

## Product Purpose

Mnemo is a personal AI bookmark app. The user pastes a link in a chat. The app reads the page, writes a short summary, picks a folder and saves it. Later the user asks in plain words and gets the link back with the reason it was saved. Success: saving costs almost nothing, and the right bookmark comes back in the top 3.

## Positioning

The app is honest about what it knows. A summary is only written from text the app saw. A guess is labelled "guess". The app proposes and never moves or deletes alone. A neighbouring bookmark tool that hides its uncertainty could not truthfully copy this.

## Operating Context

- Two screens: Chat and Bookmark page (UI-01). The phone also has a Settings tab, which holds the theme control (see the theming spec). The laptop Settings screen is not designed.
- The bookmark page has three views: Ledger (list), Cards (grid) and Compact (D-015, F-05).
- Runs on the owner's computer first (D-007), online later (phase A).
- Used in short moments: saving a link mid-task, and asking "what do I already have about this?".

## Capabilities and Constraints

- Screens are thin. The server holds the API key and the data (D-002, NF-01).
- Touch targets at least 44px, text contrast at least 4.5:1, focus always visible, no sideways scroll at 390px width (NF-05, UI-02 to UI-05).
- Light, Dark and System themes. System is the default. The choice is remembered on the device (D-019, UI-08).
- Every colour comes from a token. No colour is written inside a component rule (UI-09).
- Fonts named by the design: Newsreader, Public Sans, Spline Sans Mono. They are self-hosted (D-026, Q-16): loading them from Google Fonts would conflict with local-first and offline use.
- Undecided: cover images, laptop Settings screen, wording of empty and error states, where the theme choice is saved (Q-15, frontend-ui open questions).

## Brand Commitments

- Name: Mnemo. Other software uses the name, so re-check before any public release ([naming](docs/research/naming.md)).
- Visual direction is binding: **V3, the ledger** (D-016). Serif headings, the folder in the margin, "guess" labels. Mockup variants V1, V2, V4 and V5 are dropped.
- The owner rejected earlier mockups as "AI slop". Generic AI-looking output is a known failure here.

## Evidence on Hand

- Colour tokens with contrast numbers: [theming spec](docs/feature-specs/theming-and-design-tokens.md). The numbers were measured on the mockup, not on a built page.
- Mockup (light, dark, laptop, phone): https://claude.ai/artifact/7Q93Na93mLjP5FCbWbeYwz. It is not a permanent store, and it was never checked as a rendered page.
- 20 sample links: [sample links](docs/reference/sample-links.md).
- Absent: no built UI yet, no real bookmark data, no real `og:image` coverage test. Do not invent screenshots, usage numbers or testimonials.

## Product Principles

1. Saving must cost almost nothing.
2. Be right, or say you are not sure. Never show a summary of text the app did not see.
3. The user stays in control: the app proposes, Move and Undo are always visible.
4. Give something back every week.
5. The page must not look like generic AI output. Specific, calm and dense beats decorative.

## Accessibility & Inclusion

Required standard from NF-05: 44px touch targets, 4.5:1 text contrast (3:1 for control borders), visible focus in both themes, works at 390px. Every empty and error state has text, never a blank area. Keyboard reach to every control (frontend-ui acceptance criterion 4).
