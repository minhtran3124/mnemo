# Decision Log
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file records the big decisions for Mnemo in a short ADR style (ADR means architecture decision record). Each row has context, decision, status and consequences.

Status values: Accepted (agreed), Proposed (suggested, not yet built or agreed), Open (not decided).

| ID | Context | Decision | Status | Consequences |
| --- | --- | --- | --- | --- |
| D-001 | You chose to use only the Claude API. | Claude API only. | Accepted | Anthropic has no embedding API (lesson 34), so search uses no embeddings (D-006). Page text, URL and questions go to Anthropic. |
| D-002 | Anyone can read the code of a web page or an app (lessons 1 and 2). | The server holds the API key. Screens never hold it. | Accepted | One small Python server plus thin screens. See NF-01. |
| D-003 | The first idea was a command line. | Two screens: chat and bookmark page. | Accepted | Mock-ups in the plan use terminal text only to stay short. |
| D-004 | Claude could be wrong about whether text is a link or a question. | Plain code (a URL check) decides link versus question. | Accepted | This choice cannot be wrong in the way a model can. |
| D-005 | Auto-filing can hide a bookmark in the wrong folder. | Claude picks only from existing folders; Unsorted when unsure; code rejects unknown folder names; Move and Undo always visible; search ignores folders. | Accepted | Filing accuracy is measured on the Route set. See [safe auto-filing](../solutions/safe-auto-filing.md). |
| D-006 | Claude API only means no embeddings. | Chunk page text, rewrite the query, two BM25 indexes, merge with RRF, Claude picks the best 3. | Accepted | Search may be weaker for questions with very different words. The phase 5 eval shows how much. The query rewrite and pick step are the plan's own design, not in the course. See [embeddings alternatives](../research/embeddings-alternatives.md). |
| D-007 | Work is safest on your own computer first. | Local first, Render later. | Accepted | Render price and disk persistence are unverified. See [hosting check](../research/hosting-check.md). |
| D-008 | A native iPhone app needs Swift and, for a stable install, a paid Apple account. | iPhone Share Shortcut, not a native app. | Accepted | Whether the Shortcut works is unverified; test early. Fallback: paste in Safari. |
| D-009 | A browser tab does the same job as a window app. | The .deb app is phase C and is cut first. | Accepted | Low value; outside the course. |
| D-010 | A .dmg only works on a Mac and shows a warning when unsigned. | Mac .dmg is not planned. | Accepted | Add only if you ask. See [open questions](../research/open-questions.md). |
| D-011 | Your English is better for reading than writing. | English-only summaries in version 1. | Accepted | No language badge in version 1. The Vietnamese tutorial stays in the set as an extra case, not scored. `language` field is not in version 1. |
| D-012 | The host may not keep files between deploys. | All storage goes through `store.py`. | Accepted | If the host loses files, only the inside of `store.py` changes (to a database). See NF-03. |
| D-013 | Two sample links did not fit the seven types. | Add types `docs` and `other`. | Proposed | Not yet built. The eval will show if more types help. |
| D-014 | The project needed a name. | The name is Mnemo (was Bookmark Brain). | Accepted | Other software uses the name. Re-check before any public release. See [naming](../research/naming.md). |
| D-015 | People scan lists in different ways. | The bookmark page has a Grid, List and Compact switcher (F-05). In the V3 mockup, List is called Ledger and Grid is called Cards. | Accepted | Grid and List in phase 1; Compact in phase 3. The CSS `:has()` approach is unverified. |
| D-016 | Five mockups (V1 to V5) exist, and earlier ones felt like "AI slop". | Visual direction is V3, the ledger (serif, folder in the margin, "guess" labels). | Accepted | You chose V3 after seeing it in light and dark. V1, V2, V4, V5 are dropped. Unverified: it was chosen from mockups, not from real links in a running page. Re-check after phase 1. See [design review](../reviews/design-review-v1-v5.md). |
| D-017 | Page text goes to the API even for links you want to keep private. | Private mode (F-19): a link marked private is saved as link only and nothing is sent to the API. | Proposed | Ships in phase 3 if accepted. Adds a `private` field (proposed). |
| D-018 | Page text goes to the API. | Public links only while building. | Accepted | Check your company's AI policy before saving work links. |
| D-019 | The page must be comfortable in a bright room and at night. | Light and dark themes. Default: follow the system setting. The user can override with Light or Dark, and the choice is remembered on the device. | Accepted | Needs a token set for both themes. See [theming spec](../feature-specs/theming-and-design-tokens.md). Contrast was measured on the mockup colours only; measure again in the real page. |
| D-020 | The UI needs design checks, and the owner is not a designer. | Use Impeccable (`npx impeccable`) for UI work. `PRODUCT.md` holds product truth for design commands. Its design hook checks UI edits in Claude Code. | Accepted | Node is needed for dev tools only. The server stays Python. Setup: see the README. `DESIGN.md` is not written until a UI exists. The hook's rules must not override D-016 (V3) or UI-09 (tokens). |
| D-021 | Phase 1 needs a web server, and the stack was not chosen. | FastAPI with Uvicorn, uv, plain HTML/CSS/JS pages with no build, pytest and ruff, bm25s for search, httpx and trafilatura for fetching, pypdf for PDFs. Details in [tech stack](../product/tech-stack.md). | Accepted | PyMuPDF is not used (AGPL). `rank-bm25` is not used (unmaintained since 2022). Render disk pricing still open (Q-01). |
| D-022 | Four details of the stack needed a decision: the HTTP client, the search library, how the MCP server writes, and the model for saving. | Use httpx2 for fetching. Wrap bm25s to give add_document() and search(). The MCP server calls the web server's HTTP API, so the web server is the only writer. Use Haiku 5.5 for save.py. | Accepted | Both SDKs already depend on httpx2. The bm25s wrapper rebuilds the index on change. Haiku 5.5 fits the $10 budget at the assumed volume (see tech stack). Re-check the save score in the eval. |
| D-023 | A `.env.example` is a common habit, but a pre-commit hook that allows one is also a hole for a real key. | The hook blocks every staged `.env*` file, including `.env.example`, deletions and renames. New variables are listed in `README.md`, not in a committed example file. | Accepted | A contributor cannot commit a placeholder env file. Removing a leaked `.env` from git needs `git commit --no-verify`. See [git and secrets](git-and-secrets.md). |
| D-024 | The plan put CI in phase A, but the autopilot merge gate fails when a PR has no CI check. | A GitHub Actions workflow runs `ruff` and `pytest` on every pull request, from phase 0. | Accepted | The workflow is the minimum. Phase A can add more checks. See [tech stack](../product/tech-stack.md). |
| D-025 | The course gets clean JSON with prefill and a stop sequence, but the official page says prefill is incompatible with JSON outputs, and the SDK has `messages.parse()`. | Use structured outputs: `client.messages.parse(output_format=Model)`, result in `parsed_output`. No prefill, no stop sequence, no `temperature`. Code still checks tag count and summary length. | Accepted | `claude-haiku-5-5` supports it. Cannot be combined with citations, so phase 6 quotes need another way. See [api notes](../reference/api-notes.md) item 13. |

## How to change a decision
1. Write the new row or change the status.
2. Say what changed in your [session note](session-log-template.md).
3. Update the specs that mention the decision.

## Open items
- D-016 and D-019 are Accepted. Re-check them after phase 1 with real links in a rendered page.
- D-020: when the first page is built, run `/impeccable document` to write `DESIGN.md` from the real tokens, and check that the detector does not flag the V3 fonts or tokens.
- D-013 and D-017 are Proposed. Confirm or reject them before phase 3.

Related: [open questions](../research/open-questions.md), [risk review](../reviews/risk-review.md).
