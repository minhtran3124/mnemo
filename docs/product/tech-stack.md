# Tech stack
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file chooses the tools for each layer of Mnemo. Decision: D-021. It follows the rules already set in the PRD and specs (D-001, D-002, D-006, D-007, D-012, NF-03).

Visual page: [Architecture](https://claude.ai/artifact/HRJ54QxYXpooHoemp6uSgV). It is a snapshot of `main` at commit `ce40e28` and is private until you share it. This file is the source of truth; if they differ, fix the page.

Versions are the latest on PyPI and npm at the research date (2026-11-04). Pin the exact versions in the lockfile when you install them. Nothing here is tested in a running app yet.

## Stack by layer

| Layer | Choice | Version (research date) | Why |
| --- | --- | --- | --- |
| Language | Python | 3.12 (the local machine has 3.12.3; pydantic-settings and python-multipart need 3.11 or newer) | D-001 course; the plan is Python |
| Packages and env | uv | 0.13.7 | One tool for venv, install and lockfile (`uv.lock`) |
| Backend (HTTP) | FastAPI + Uvicorn | FastAPI 0.162.0, Uvicorn 0.54.0 | Type hints and automatic validation; serves the thin pages (D-002) |
| Data validation | Pydantic + pydantic-settings | Pydantic 2.14.2, pydantic-settings 2.16.2 | Validates records before `store.py` writes them (DM-02); reads `.env` and `config.py` values |
| Form and file upload | python-multipart | 0.0.33 | Needed by FastAPI for uploads (PDF, screenshots; phases 4 and 6) |
| Claude API | Anthropic Python SDK | 2.4.0 | The only model provider (D-001). JSON output via `client.messages.parse()` with a Pydantic model (verified in the SDK source) |
| MCP server | MCP Python SDK (`MCPServer`, in mcp 2.x; the old `FastMCP` name was removed) | 2.3.0 (MIT) | Phase 9. The MCP server calls the web server's HTTP API, which uses `store.py`; it does not write files itself (decision D-022) |
| Web fetch | httpx2 | 2.16.0 | Timeouts, redirects and size limits in one client (PR-03, PR-05). Chosen (D-022): `anthropic` and `mcp` already depend on it, so the app runs one HTTP stack. Verified by names only: `Client`, `Timeout`, `follow_redirects`, `max_redirects`, `stream`. Run a test fetch before relying on it |
| Page text extraction | trafilatura | 2.3.1 | Main text and metadata from HTML (PR-01 to PR-05) |
| PDF text | pypdf | 6.21.4 | Plain text for PDFs in phase 6; BSD-3-Clause |
| Search | bm25s | 0.3.16 | BM25 for the two indexes, behind a thin wrapper that gives SE-03's `add_document()` and `search()`. The wrapper rebuilds the index after each change; this is fast enough for hundreds of bookmarks (D-022) |
| Storage (v1) | JSON and text files, written atomically | stdlib | No database in v1 (ST-02, NF-03) |
| Storage (later) | Hosted database (for example Postgres), behind `store.py` | not chosen | If the host disk does not persist, a file-based SQLite would be lost the same way. A database must live off the host (D-012) |
| Frontend | Plain HTML, CSS and a little vanilla JS, served by FastAPI | none | Thin screens (D-002). No build step. The design hook already checks `.html`, `.css` and `.js` |
| Styling | CSS custom properties from the theming spec | none | Tokens only (UI-09, D-019) |
| Lint and format | ruff | 0.17.3 | One tool for both |
| Tests | pytest + FastAPI's test client (httpx) | pytest 9.2.0 | Standard; no network in unit tests |
| Evals | Plain Python scripts in `evals/`, results as CSV | none | The eval spec is a list of rows and graders (eval-process.md); a framework adds nothing |
| Dev design tools | Node 20+, `impeccable` | impeccable 4.8.0 (npm) | Already set up (D-020); not part of the app |
| Local run | Uvicorn bound to `127.0.0.1` | none | PV-02 |
| Hosting (phase A) | Render web service on a paid instance, with a persistent disk | not priced (Q-01) | D-007 |
| Share Shortcut (phase B) | iOS Shortcuts app, no code | none | D-008 |
| Desktop window (phase C) | Not chosen yet | none | D-009 cuts it first; choose only if phase C starts |

## Libraries not chosen, and why

| Option | Reason it is out |
| --- | --- |
| Flask, Django | FastAPI already gives validation and typed handlers; Django's admin and ORM are not needed (ST-02) |
| `rank-bm25` | Last release 2022-02-16. `bm25s` is maintained and fast |
| PyMuPDF (`pymupdf`) | Dual-licensed AGPL-3.0 or commercial. Phase A puts the app on a public host, and AGPL network clauses would then apply. Use pypdf |
| React, Vue, Next.js, a bundler | The pages are thin and need no build. A framework adds a second language and a build step for little gain |
| A database server (Postgres) | Not needed in v1 (ST-02); phase A decides after the disk check |
| Vector database, embeddings | Out by D-001 and D-006 |
| LangChain or similar agent frameworks | Not needed; the pipeline is a few explicit steps (search-no-embeddings.md) |

## Repository layout (proposed)

The layout follows the specs, not a generated template. Build it in phase 0 and 1.

```text
app/            FastAPI app, routes (thin)
store.py        the only module that touches data/ (NF-03)
config.py       model name, max_tokens, page length limits (NF-02)
fetcher/        page fetch and GitHub API (PR-01)
save.py         Claude call for a card (phase 1)
search.py       BM25 indexes, RRF, pick step (phase 5)
mcp_server.py   MCP server (phase 9)
web/            HTML, CSS, JS pages (no build)
evals/          golden sets, graders, results CSV (phase 2)
tests/          pytest
data/           local bookmarks, pages, log (gitignored)
```

## Model choice and monthly cost

Prices verified on the [Anthropic pricing page](https://platform.claude.com/docs/en/about-claude/pricing), per million tokens (input / output):

| Model | Input | Output |
| --- | --- | --- |
| Claude Haiku 5.5 | $0.10 | $0.50 |
| Claude Sonnet 5.5 | $2 | $10 |
| Claude Opus 5.5 | $4 | $20 |
| Claude Fable 5.1 | $10 | $50 |

Estimate for `save.py` only (assumptions, not measured: 8,000 input and 500 output tokens per save, 300 saves per month; the PRD sets no monthly volume):

| Model | API per month | With hosting at about $7 (unverified) | Fits $10? |
| --- | --- | --- | --- |
| Haiku 5.5 | about $0.30 | about $7.30 | Yes |
| Sonnet 5.5 | about $6.30 | about $13.30 | No |
| Opus 5.5 | about $12.60 | about $19.60 | No |

Chosen (D-022): Haiku 5.5 for `save.py`. Re-check the score in the eval; move to a bigger model only if the save score fails and the budget allows it. Set the model name in `config.py` (NF-02).

## Commands (once the code exists)

| Task | Command |
| --- | --- |
| Install | `uv sync` |
| Run locally | `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` |
| All tests | `uv run pytest` |
| One test | `uv run pytest tests/test_store.py::test_name` |
| Lint and format | `uv run ruff check . && uv run ruff format --check .` |
| UI design scan | `npm run design:detect` (once `web/` exists) |

The module path `app.main:app` is a proposal. Keep it in sync with the real layout.

## Hosting and DevOps

- **Phase 0 to 4:** run on your own computer, bound to `127.0.0.1` (D-007).
- **Phase A:** Render, as planned. Verified in [Render persistent disks](https://render.com/docs/disks): the disk attaches to a paid web service, keeps files across deploys and restarts (only under the mount path), takes a snapshot every 24 hours, keeps snapshots 7 days, and allows only one instance. Price: Unverified (Q-01); the official page lists no per-GB price.
- **Data risk:** the disk persists, but `bookmarks.json` is rewritten whole on each save. Use one worker plus a file lock in `store.py`, and export data off the host on a schedule (storage.md).
- **Backups:** copy `data/` on a schedule. How often is an open question (storage.md).
- **Secrets:** the key is an environment variable on the host, never in the repo (NF-01). A pre-commit check for keys is listed in git-and-secrets.md.
- **CI:** `.github/workflows/ci.yml` (added in phase 0, #9) runs `uv sync --locked`, `ruff check`, `ruff format --check` and `pytest` on every pull request and on pushes to `main`. The autopilot merge gate needs a CI check on each PR.

## Notes and open items

- **PyMuPDF licence:** AGPL-3.0 or commercial. This is why pypdf is chosen.
- **pypdf licence:** BSD-3-Clause (checked in the wheel metadata).
- **Two writers:** the MCP server (phase 9) runs as a separate process. If it writes through `store.py` while the web server runs, `store.py` needs a lock or the MCP server must call the HTTP API instead. Open question.
- **Claude JSON output:** use structured output (`messages.parse()`, or `output_config.format` on the API) instead of prefill. This is documented and validates the schema. Whether prefill still works on current models is not verified; the choice does not depend on it.
- **Temperature:** do not set `temperature` in `config.py` until the current model docs confirm it is accepted (unverified).
- **Phase A login:** not chosen. SA-03 and PV-03 need a method (for example one token checked by middleware).
- **Render pricing and sleep behaviour:** Unverified. See hosting-check.md.
- **Anthropic SDK and model names:** check the current model names and prefill support before phase 0 (api-notes.md, items 1 and 4).
- **Frontend fonts:** self-hosting or Google Fonts is still open (Q-16).
