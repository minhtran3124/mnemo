# mnemo

A personal AI bookmark app. Paste a link in a chat, the app reads the page, summarises it and files it. Ask in your own words to find it again. Docs: [docs/README.md](docs/README.md). Product record for design work: [PRODUCT.md](PRODUCT.md).

The server is Python. A small Node setup (`package.json`) holds dev tools for the web UI only.

## Setup when you start the project

You need Node 20 or newer (`node -v`) and Claude Code.

1. Install the dev tools:

   ```bash
   npm install
   ```

2. Install the Impeccable design skills into Claude Code (D-020). This writes into `.claude/`:

   ```bash
   npm run design:install
   ```

3. Turn on the secrets pre-commit hook (once per clone). It blocks any staged file whose name starts with `.env` and any added line that looks like an Anthropic key. `git commit --no-verify` skips it, so do not use that flag:

   ```bash
   git config core.hooksPath .githooks
   ```

4. Restart Claude Code in this folder so it loads the new skill and hooks. Approve the hooks when asked.
5. Check the design hook is on (in the Claude Code chat):

   ```
   /impeccable hooks status
   ```

   If it is off, run `/impeccable hooks on`.

`PRODUCT.md` already exists. Do not run `/impeccable init` again unless the product facts changed.

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
| `npm run design:detect` | Scan the `web/` folder for UI design problems (once it exists) |

## Rules to keep

- The design direction is V3, the ledger (D-016). Colours come from tokens only (UI-09). Impeccable suggestions must not break these.
- If `PRODUCT.md` and `docs/feature-specs/frontend-ui.md` disagree, fix both in the same session.

## Environment variables

Put these in a local `.env` file in the repo root. It is gitignored, and the pre-commit hook blocks every `.env*` file, so do not commit one.

| Variable | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Your Claude API key. Read by `config.py`. Never print it or paste it in a chat. |
