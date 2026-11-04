# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

Mnemo is a personal AI bookmark app (paste a link, get a summary and a folder, find it again by asking). The repo is **docs only**: no Python, HTML or tests exist yet, and phase 0 has not started. There is no build, lint or test command for the app. The design lives in `docs/`, and `docs/README.md` is the entry point. Read `docs/product/phases-overview.md` and the current phase plan in `docs/product/plans/` before writing code.

The only runnable commands are the Node dev tools for UI design checks (`package.json`):

- `npm install`, then `npm run design:install`: install the Impeccable skills into `.claude/` (generated and gitignored; restart Claude Code afterwards).
- `npm run design:update` / `design:check`: update the skills / check for an update.
- `npm run design:detect`: scan `web/` for UI design problems (the folder does not exist yet).

## Docs rules

- IDs are used across all docs: features `F-xx`, non-functional `NF-xx`, decisions `D-xxx` (`docs/process/decision-log.md`), open questions `Q-xx` (`docs/research/open-questions.md`), UI rules `UI-xx`. Cite them instead of restating.
- Anything not checked is marked **Unverified** or **Open question**. Never turn an unverified claim into a fact. If a fact is missing, add an open question.
- Plain English, no calendar dates (phases and sessions only).
- If a doc and the code disagree, fix the doc in the same session. When a UI decision changes, update `PRODUCT.md` and `docs/feature-specs/frontend-ui.md` together.
- Changing a decision: edit the decision log row, then the specs that mention it.

## Architecture rules that span the design

The planned system is a small Python server plus thin web pages (Chat, Bookmark page). These rules come from several specs and are easy to break:

- **The server holds the API key; pages never do** (D-002, NF-01). The server binds to `127.0.0.1`, never `0.0.0.0`. The key lives only in `.env`, which is gitignored.
- **All bookmark access goes through `store.py`** (NF-03, D-012): the only code that touches `data/bookmarks.json`, `data/pages/<id>.txt` and `data/log.jsonl`. Writes are atomic (temp file, then rename). The inside can later become a database without changing callers.
- **Plain code, not Claude, decides link versus question**: a URL regex (D-004, CI-02). A message with a URL is a save; two URLs save two bookmarks.
- **Honest failure** (NF-04, F-02): if a page cannot be fetched or the text is too short, save the link only with `page_status = unreadable` and `summary = null`. Never write a summary of text the app did not see. A reason written by the app is marked `guess` (`reason_source`).
- **Filing is safe by construction** (D-005): Claude picks only from existing folders, otherwise `Unsorted`; code rejects unknown folder names; Move and Undo are always visible; the app proposes and never moves or deletes alone.
- **Search uses no embeddings** (D-001, D-006): chunk page text, rewrite the query, two BM25 indexes merged with RRF, then Claude picks the best 3.
- **Cost limits** (NF-02): `max_tokens` and a maximum page length live in one `config.py`, as does the model name.
- **Public links only while building** (D-018): page text goes to the Claude API.

## UI work

- `PRODUCT.md` is the product record that Impeccable design commands read. Visual direction is fixed: **V3, the ledger** (D-016), with light, dark and system themes (D-019). Colours come from the tokens in `docs/feature-specs/theming-and-design-tokens.md` only, never inside a component rule (UI-09).
- Accessibility floor (NF-05): 44px touch targets, 4.5:1 text contrast, visible focus, no sideways scroll at 390px.
- The design hook (`.claude/settings.local.json`) checks UI edits after Edit/Write. Fix real findings; do not add ignores just to silence it.
- `DESIGN.md` does not exist yet. Write it with `/impeccable document` after the first page is built.

## Working agreements

From `docs/process/working-agreements.md`: sessions are about 30 minutes, one change at a time, plan before code, small commits, and a short session note at the end (`docs/process/session-log-template.md`). Do not start the next phase until the current phase check in `docs/process/definition-of-done.md` passes. Review code like a tester: run a good input and a bad input, and confirm an unreadable page gives no summary.

## Git

- The remote is named `github`, not `origin`. Use `git push -u github HEAD`.
- Work on a branch and open a PR; `main` is the base.
