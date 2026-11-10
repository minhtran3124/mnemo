# Phase 0: Setup
Status: Draft v0.1 · Owner: KhoiTran · Phase: 0

Make the project safe and ready, so later phases do not stop on setup problems.

## Goal
A project folder `mnemo/` where a script talks to Claude, and the API key is safe.

## You can now
Nothing visible yet. The project is safe and ready.

## Sessions and lessons
1 session. Lessons 1-5, 58, 59.

## Inputs
- A Claude API account and key (Claude API only, D-001).
- Python installed. Claude Code installed.
- Decision: use public links only while building (D-018).

## Tasks
1. Create `mnemo/` as a git repo. Add `.gitignore` with `.env` in it. See [git and secrets](../../process/git-and-secrets.md).
2. Put the API key in `.env`. Install the SDK. Run `git status` to confirm `.env` is not tracked.
3. Write `mnemo/core/config.py`: model name (one place), `max_tokens`, max page length. Check current model names in the official docs (checked in phase 0, see [API notes](../../reference/api-notes.md) item 1).
4. Write `mnemo/core/client.py` with helpers: messages, `system`, `temperature`, `stop_sequences`.
5. Write `CLAUDE.md`: Python, plain files, all storage through `mnemo/core/store.py`, never print the key, bind server to 127.0.0.1.
6. Write a test script: one call, then a second call with the history. Claude must remember a fact from the first call.
7. In the Claude Console, set a monthly spending limit if your account offers one (NF-02).

## Done when
- [ ] The script prints an answer from Claude.
- [ ] The second call (with history) shows Claude remembers the first fact.
- [ ] `.env` is not in git (`git status` and `git log` show no key).
- [ ] `CLAUDE.md` exists and lists the rules above.

## Risks
Key leaks into git (NF-01). Wrong model name. See [risk review](../../research/risk-review.md).

## If time runs short
Skip the spending limit for now (but set it before phase A). Do not skip the `.gitignore`.

## Links to specs
[privacy and security](../../feature-specs/privacy-and-security.md) · [storage](../../feature-specs/storage.md) · [API notes](../../reference/api-notes.md) · [phases overview](../phases-overview.md)
