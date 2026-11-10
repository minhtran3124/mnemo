# Structure review: code layout after the package move

Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This note records a read of the repo layout right after the move into the `mnemo/` package. It finds what is confusing and says what was fixed and what waits. Paths below are checked against the tree unless marked **Unverified**.

## Fixed in the restructure

| Where | Problem | Fix |
| --- | --- | --- |
| `mnemo/core/config.py`, `mnemo/fetcher/__init__.py`, `evals/run_eval.py` | Comments named `save.py`, now `mnemo/save/pipeline.py`. | Comments reworded. |
| `mnemo/api/server.py`, `tests/api/test_chat_page.py` | Comments named `web/`, now `mnemo/api/web/`. | Comments reworded. |
| `docs/testing/phase1-links-check.md` | Gave `uv run python server.py`, which no longer works. | Now `uv run python -m mnemo.api.server`. |
| `README.md` | Layout text used short names. | Full paths. |
| `STATUS.md` | Said phase 2 follow-ups were not started; later commits show phase 4 work. It was never committed. | Deleted at the owner's request. |

## Fix later, as its own change

| Where | Problem | Suggested fix |
| --- | --- | --- |
| `mnemo/api/server.py` (507 lines) | Four jobs in one file: HTML page building, error and host middleware, the JSON API, and chat orchestration (`chat()` holds about 55 lines of logic). `.claude/rules/backend.md` says handlers stay thin. | Split into `pages.py`, `errors.py` and route modules inside `mnemo/api/`. |
| `evals/golden.py` and `evals/golden/` | A module and a folder share one name. | Rename the folder to `golden_pages/`. How many references use the old name is **Unverified**. |
| `tests/process/` | The name is vague. It tests `scripts/` and `.githooks/`. | Rename to `tests/repo_tools/`. Optional. |

## Fine as is

- `mnemo/core/store.py` (401 lines) holds bookmarks, the chat log and the event log. That is one door to storage, as `CLAUDE.md` requires. It can become a package later without changing callers.
- `mnemo/save/pipeline.py` holds preview, save, fill-in and folder resolving. These are one flow.
- `mnemo/chat/` holds `intent.py` on `main`. Phase 4 adds the ask loop, tools and link import there: all things the chat box does. That phase 4 code was judged from its names only (**Unverified**).
- `mnemo/fetcher/`, `mnemo/core/urlclean.py`, and `evals/prompts/` vs `mnemo/save/prompts/` each have one clear purpose.
- `tests/` mirrors `mnemo/`. `PRODUCT.md` stays at the root because the design tooling reads it. `scripts/check_memory.py` is the phase 0 proof and stays.

## Docs layout change

`manual-testing/` became `testing/` and took the eval process and the golden sets. `reviews/` merged into `research/` (and the pre-start checklist into `process/`). `product/plans/` became `plans/`. The reason: four folders overlapped, and test material sat in four places. See the folder map in [docs/README.md](../README.md).
