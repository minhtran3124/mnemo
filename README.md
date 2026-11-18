# mnemo

A personal AI bookmark app. Paste a link in a chat, the app reads the page, summarises it and files it. Ask in your own words to find it again. Docs: [docs/README.md](docs/README.md). Product record for design work: [PRODUCT.md](PRODUCT.md).

The server is Python. A small Node setup (`package.json`) holds dev tools for the web UI only.

## Prerequisites

- **uv** (Python package and project manager). Install it from https://docs.astral.sh/uv/. Check with `uv --version`.
- **Python 3.12**. The version is pinned in `.python-version`, and uv uses it for this project.
- **Node 20 or newer** (`node -v`). Only needed for the design dev tools.
- **Claude Code**, for the design skills and hooks.
- **A Claude API key** from the Claude Console (https://platform.claude.com). Needed to save links and to chat.

## Setup when you start the project

Run these steps once after a fresh clone, from the repo root.

1. Install the Python dependencies:

   ```bash
   uv sync
   ```

2. Add your API key. Create a file named `.env` in the repo root with this line, and put your key after the `=` sign:

   ```text
   ANTHROPIC_API_KEY=your-key-here
   ```

   `.env` is gitignored. Never paste the key into a chat, a commit or a log.

3. Install the dev tools:

   ```bash
   npm install
   ```

4. Install the Impeccable design skills into Claude Code (D-020). This writes into `.claude/`:

   ```bash
   npm run design:install
   ```

5. Turn on the secrets pre-commit hook (once per clone). It blocks any staged file whose name starts with `.env` and any added line that looks like an Anthropic key. `git commit --no-verify` skips it, so do not use that flag:

   ```bash
   git config core.hooksPath .githooks
   ```

6. Restart Claude Code in this folder so it loads the new skill and hooks. Approve the hooks when asked.
7. Check the design hook is on (in the Claude Code chat):

   ```
   /impeccable hooks status
   ```

   If it is off, run `/impeccable hooks on`.

`PRODUCT.md` already exists. Do not run `/impeccable init` again unless the product facts changed.

## Run the app

```bash
uv run python -m mnemo.api.server
```

Then open http://127.0.0.1:8000 in your browser. The pages are:

- `/` is the chat.
- `/bookmarks` lists your saved links.
- `/settings` holds the settings page.

Stop the server with Ctrl+C.

- The server binds to `127.0.0.1` only (uvicorn's default port, 8000), so just this computer can reach it. A request that names any other host gets a 403 `forbidden_host` error.
- The server starts without `ANTHROPIC_API_KEY`, but saving a link and chatting need it.
- Bookmark data is stored under `data/`. The folder is gitignored, and the app creates it as needed.
- Every error uses the format `{"error": {"code": ..., "message": ...}}`.

## Project layout

```text
mnemo/
  core/      config, Claude client, store (the only code that touches data/), URL cleaning
  chat/      intent, ask loop and tools, link import
  save/      the save pipeline and its versioned prompts (save/prompts/)
  fetcher/   page fetch and the GitHub API
  api/       FastAPI server and the web pages (api/web/, no build)
evals/       golden sets, graders, eval prompts, results CSV
scripts/     one-off checks (memory check)
tests/       pytest, in folders that mirror mnemo/
docs/        specs, plans, testing, decisions
data/        your bookmarks (gitignored)
```

Modules import each other as `from mnemo.core import store`.

## Check the code

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

The tests use fake Claude clients, and a search of `tests/` finds no live API calls. Run the memory check below only when you want a real API check.

## Daily commands (in the Claude Code chat)

| Command | Use it to |
| --- | --- |
| `/impeccable shape <screen>` | Plan a screen before you build it |
| `/impeccable critique` | Get a design review of what exists |
| `/impeccable audit` | Check accessibility and quality |
| `/impeccable polish` | Final pass before you finish a screen |
| `/impeccable document` | Write `DESIGN.md` from the built UI (do this after phase 1) |

## npm scripts

| Script | What it does |
| --- | --- |
| `npm run design:install` | Install or repair the Impeccable skills for Claude Code |
| `npm run design:update` | Update the skills to the latest version |
| `npm run design:check` | Say whether an update is available |
| `npm run design:detect` | Scan the `mnemo/api/web/` folder for UI design problems (once it exists) |

## Memory check

`uv run python scripts/check_memory.py` makes two real Claude calls and checks that the second answer remembers a fact from the first. It prints `memory check: PASS` and exits 0, or prints `memory check: FAIL` and exits 1. It exits 2 if `ANTHROPIC_API_KEY` is not set, and exits 3 with `memory check: ERROR` if an API call fails (bad key, network, timeout). It costs money, so CI does not run it.

## Rules to keep

- The design direction is V3, the ledger (D-016). Colours come from tokens only (UI-09). Impeccable suggestions must not break these.
- If `PRODUCT.md` and `docs/feature-specs/frontend-ui.md` disagree, fix both in the same session.

## Environment variables

Put these in a local `.env` file in the repo root. It is gitignored, and the pre-commit hook blocks every `.env*` file, so do not commit one.

| Variable | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Required for saving and chat. Your Claude API key, read by `mnemo/core/config.py`. Never print it or paste it in a chat. |
| `GITHUB_TOKEN` | Optional. A GitHub token, sent only to the GitHub API (`https://api.github.com`) when reading GitHub pages. |
