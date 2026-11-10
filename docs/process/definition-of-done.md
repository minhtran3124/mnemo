# Definition of Done
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file says when a feature and a phase count as done. "Done" means a person has checked it, not only that code exists.

## A. Done for the package and docs restructure

Each item can be checked by running the command or reading the file. Evidence is what the command printed.

- [x] Tests pass: `uv run pytest` → `291 passed` (on `main`, which does not yet have the 23 phase 4 tests).
- [x] Lint and format are clean: `uv run ruff check . && uv run ruff format --check .` → `All checks passed!`, all files already formatted.
- [x] No broken relative link: `uv run python scripts/check_links.py` → `checked 448 relative links, 0 broken`.
- [x] The old doc folders are gone: `ls docs/manual-testing docs/reviews docs/feature-specs/test-cases docs/product/plans` → `No such file or directory`.
- [x] Every folder in `docs/` has a row in the folder map of [docs/README.md](../README.md): `for d in docs/*/; do grep -q "\`$(basename $d)/\`" docs/README.md || echo MISSING $d; done` → prints nothing.
- [x] The seven known conflicts are settled or listed as an **Open question** in [docs/README.md](../README.md) (section "Conflicts between docs"): `grep -c "Open question" docs/README.md` prints a number above 0.
- [x] No old-layout path is left: `grep -rnE "python server\.py|save\.py" README.md CLAUDE.md docs evals mnemo tests --include='*.md' --include='*.py'` → hits only in `decision-log.md` (history), the structure review and this file, which quote the old names.
- [x] Storage goes only through the store: `grep -rn "data/" mnemo --include='*.py' | grep -v core/store.py` → one hit, a comment in `mnemo/core/config.py`, no file access.
- [x] The structure review is written down: [structure-review](../research/structure-review.md).
- [x] The moves kept history: `git log --follow docs/testing/test-strategy.md` shows commits from before the move.
- [x] No attribution in commits: `git log main..HEAD --format=%B | grep -ciE "co-authored-by|generated with"` → `0`.
- [ ] The PR targets `main`, is open, and is not merged by the agent. Waiting for the owner to approve the push.

## B. Done for any future change

- [ ] `uv run pytest` exits 0.
- [ ] `uv run ruff check . && uv run ruff format --check .` exits 0.
- [ ] `uv run python scripts/check_links.py` prints `0 broken`.
- [ ] Docs match the code: every path a changed doc names exists (`ls` it), and no **Unverified** tag stays on a fact the change checked.
- [ ] No secret in the diff: `git diff main... | grep -E "sk-ant|ANTHROPIC_API_KEY=."` prints nothing, and `git config core.hooksPath` prints `.githooks`.
- [ ] Storage goes only through the store: `grep -rn "data/" mnemo --include='*.py' | grep -v core/store.py` shows no file access.
- [ ] Honest failure still holds: `uv run pytest tests/save/test_save.py tests/evals/test_run_eval_honesty.py` passes, and a link-only save has a null summary.
- [ ] Safe filing still holds: `uv run pytest tests/save/test_filing.py tests/api/test_move_undo_api.py` passes.
- [ ] Commit messages and the PR body have no `Co-Authored-By` trailer and no "Generated with" line: `git log main..HEAD --format=%B | grep -ciE "co-authored-by|generated with"` prints `0`.
- [ ] The branch is pushed to the `github` remote only, after `gh pr view <n> --json state` shows `OPEN`. The owner merges, not the agent.

## Per feature
A feature is done when all rows are true.

| # | Check |
| --- | --- |
| 1 | Every requirement in the feature spec has a passing check (code, eval or manual). |
| 2 | Acceptance criteria in the spec pass. |
| 3 | The feature works on a readable link and on an unreadable link. |
| 4 | An error shows a clear message in plain English, not a crash. |
| 5 | The API key is not in any new file, log line or page. |
| 6 | Cost limits still apply: `max_tokens` and a maximum page length (NF-02). |
| 7 | Bookmarks are read and written only through `mnemo/core/store.py` (NF-03). |
| 8 | A guess is marked as a guess (NF-04). |
| 9 | The [smoke checklist](../testing/smoke-checklist.md) passes. |
| 10 | The change is committed, with a note in the session log. |
| 11 | Docs that describe the feature are updated. |

## Per phase
| Phase | Done when |
| --- | --- |
| 0 | A script gets an answer from Claude; a second call with history shows memory; the key is in `.env` and not in git. |
| 1 | A page on your computer has a chat box and a bookmark page; 5 public links give readable cards; an unreadable page is saved as link only; you found no invented fact. |
| 2 | One command scores 20 saved pages and prints three numbers; baseline ran twice; you read 3 results. |
| 3 | 3 or more prompt versions compared, one change at a time; Route set scored; unsure links go to Unsorted; Move and Undo work; tried on 10 real saves. |
| 4 | 15 questions and 3 trick questions run; every tool call gets a result; trick questions return "nothing found"; import works in small batches; screenshots save. |
| 5 | Retrieval eval compares BM25 alone, BM25 with RRF, and Claude picking; 5 planted duplicates caught. |
| 6 | A PDF is saved; an answer shows a quote that exists in the page text. |
| 7 | You accept or reject each proposed folder; nothing moves without your yes; a table compares single prompt, chain, parallel and review. |
| 8 | Digest runs on your list; every roast number equals the code count; cache fields read; thinking kept or dropped by the eval. |
| 9 | Inspector tests pass; Claude Code finds a bookmark. |
| 10 | Optional: one of dead-link doctor, CSV chart, or replacement search works. |
| A | Server online with login and spending cap; chat works in the iPhone browser. |
| B | Share from the iPhone reaches the server and the card appears. |
| C | A `.deb` file installs and opens the chat page in its own window. |

## What "done" does not mean
- A high eval score is not enough. See the [two-week user test](../testing/two-week-user-test.md).
- Code that runs once is not enough. Run it twice, with a bad input.

Related: [test strategy](../testing/test-strategy.md), [phases overview](../product/phases-overview.md).
