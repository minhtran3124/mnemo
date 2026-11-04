# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Mnemo is a personal AI bookmark app. The repo is docs only until phase 0 starts, so there is no app build or test command yet. Start at `docs/README.md`, then the current phase plan in `docs/product/plans/`. After a fresh clone run `npm install && npm run design:install` (UI design tooling, see `README.md`).

## Easy to get wrong

- The API key lives only on the server, in `.env`. Never put it in a page, log, commit or chat. The server binds to `127.0.0.1`. See `docs/process/git-and-secrets.md`.
- Bookmark data is read and written only through `store.py`. See `docs/feature-specs/storage.md`.
- Plain code (a URL regex), not Claude, decides link versus question. See `docs/feature-specs/chat-and-intent.md`.
- An unreadable page is saved as link only with a null summary. Never write a summary of text the app did not see, and mark a reason the app wrote as a guess. See `docs/solutions/honest-failure.md`.
- Filing uses existing folders or Unsorted, and the app never moves or deletes without the user. See `docs/solutions/safe-auto-filing.md`.
- No embeddings, Claude API only (D-001, D-006). Public links only while building (D-018). Decisions are in `docs/process/decision-log.md`.

## Docs and UI

- Mark anything unchecked as **Unverified** or **Open question**. When docs and code disagree, fix the docs in the same session. IDs (F, NF, D, Q, UI) are explained in `docs/README.md`.
- UI follows `PRODUCT.md` and the V3 ledger look. Colours come from tokens only: `docs/feature-specs/theming-and-design-tokens.md`.

## Workflow

- One change at a time. Plan before code. See `docs/process/working-agreements.md`.
- The git remote is named `github`, not `origin`. Work on a branch and open a PR to `main`. Check that a PR is still open before pushing to its branch.
