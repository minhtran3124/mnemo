# Eval Process
Status: Draft v0.1 · Owner: KhoiTran · Phase: 2

This file explains how to measure quality after every change. An eval is a repeatable test that gives a score. It answers one question: did the app get better or worse?

## Golden sets
A golden set is a fixed list of inputs with the answers you expect. Save the page text on disk, so each run uses the same input and not today's web.

| Set | Size | Contents | Used from |
| --- | --- | --- | --- |
| Save | 20 pages | GitHub READMEs, articles, tool pages, one unreadable page. For each: expected type, 3 to 6 expected tags, 2 to 4 key facts. | Phase 2 |
| Ask | 15 questions plus 3 trick questions | Each real question has an expected bookmark. A trick question has no answer; the right result is "nothing found". | Phase 4 |
| Route | 15 links | Each has an expected type. | Phase 7 |

The set files are in `evals/golden/`. See [test cases](golden-sets/README.md) for content.

## Held-out set
Keep 5 of the 20 save pages as a held-out set. Never use them as prompt examples. If a score rises on the other 15 but not on these 5, the gain may not be real. At least 2 of the 5 should be hard cases. `run_eval.py` prints the save quality of the held-out pages and of the tuning pages on separate lines; compare them after each run. runs.csv keeps the pooled figure.

## Baseline twice
Run the first version of the prompt two times. The gap between the two runs is your noise level. A later change must beat that gap, or you cannot say it helped.

## Noise rule
Keep a change only if the score rises by more than the noise. If it does not, undo the change.

## Four separate scores
Show four numbers side by side. Do not average them. An average can hide a drop in honesty.

| Score | What it covers |
| --- | --- |
| Save quality | Valid JSON, 3 to 6 lowercase tags, summary at most 60 words, type match, tag overlap |
| Honesty | The share of all pages in `evals/pages.json` that are honest: an unreadable page saved with a null summary, or a readable page the faithful-summary grader scored with zero unsupported statements. A readable page saved link only, with no golden text, or not scored counts as not honest |
| Find rate | Right bookmark in the top 3; trick questions return nothing |
| Folder choice | The share of the 15 Route rows where the folder Claude chose equals the expected folder in `evals/expected.json`. `Unsorted` is stored as a null folder, so null matches `Unsorted`. A made-up name is rejected by code, but the eval sees the raw model answer, so it counts as a miss. Never merge this score with the other three |

## Graders
A grader is code or a model that scores an output.
- Code graders are exact: schema, tag rules, summary length, null summary on failure, type match, tag overlap, every cited bookmark number exists.
- A model grader reads the page text and the summary, lists each statement the page does not support, and says yes or no for each key fact. The model grader can be capricious (lesson 13). The yes or no design is a plan choice, not a course rule.
- A key-fact list with a different length from the key facts is invalid output: the grader is retried once, then the page is marked `grader_failed` and not scored.

## Human check
After each run, read 3 results and the grader's reasons. If you disagree with the grader, fix the grader before you trust any score.

## Run log
One CSV row per run, in `evals/results/runs.csv`.

Run it from the repo root (it calls the real API, and writes nothing to `data/`):

```
uv run python -m evals.run_eval --run-id <id> --prompt-version <name>
```

Test the runner with the API mocked: `uv run pytest tests/test_run_eval.py -q`. A permanent API error or a missing key stops the run with exit code 1 and writes no row.

| Column | Meaning |
| --- | --- |
| run_id | A unique number or name |
| prompt_version | For example save_v2 |
| model | The model name from `mnemo/core/config.py` |
| save_quality | Score 1: share of readable pages that pass the code checks |
| honesty | Score 2: the share of all pages in `evals/pages.json` that are honest. The count of readable pages with zero unsupported statements is written to `notes`. The run prints the share and the pages honest out of all pages. |
| find_rate | Score 3. Empty until phase 4 |
| tokens_used | Total tokens for the run: the save calls plus the grader calls |
| notes | `0 unsupported: N`, the count of pages with 0 unsupported statements, then pages the faithful grader could not score, for example `0 unsupported: 9; not scored: S-03`. Pages not scored count as not honest. |

Open question: whether to add a cost column. The plan lists only the columns above.

## Baseline and noise
The unchanged save prompt (`save_v1`, model `claude-haiku-5-5`) ran twice on the 15 golden pages. 12 are readable and 3 are unreadable (S-08, S-10 and S-15). Every expected answer is still a draft.

| Run | Save quality | Mean tag overlap | Honesty (unreadable pages honest) | Pages with 0 unsupported statements | Tokens |
| --- | --- | --- | --- | --- | --- |
| baseline-1 | 0.92 (11/12) | 0.40 | 1.00 (3/3) | 11 of 12 | 124480 |
| baseline-2 | 0.92 (11/12) | 0.33 | 1.00 (3/3) | 10 of 12 | 128626 |
| Gap | 0.00 | 0.07 | 0.00 | 1 page (0.08) | 4146 |

Noise level: 0.08 (the faithful-summary count moved by 1 page of 12; save quality and honesty did not move, mean tag overlap moved by 0.07).

A later change must beat these gaps to count as an improvement.

Read 3 results with the grader's reasons (S-03, S-06 and S-09, the pages the grader failed):
- S-03 (Airtable home): failed with 2 unsupported statements in baseline-2, passed in baseline-1, and passed with 0 when graded again for this note. The grader is not stable on this page. This is the main source of the faithful-summary gap.
- S-06 (ai_agents_az repo): failed with 1 unsupported statement in baseline-1: the summary says "A GitHub repository", and the grader said the page never says it is hosted on GitHub. The page is a repo README, so this is a grader false positive. Not fixed in this phase.
- S-09 (wearedevelopers videos): failed with 3 unsupported statements in baseline-2 and passed in baseline-1 and when graded again. The summary is an index list; the grader's strictness varies from run to run.

Limits of these numbers:
- The expected tags, types and key facts are Claude-written drafts and have not been reviewed, so tag overlap (0.33 to 0.40) and type match say little yet.
- S-08 (YouTube) and S-10 (Airtable developers) failed the live fetch, so they have no text and count as unreadable. The honesty score of 1.00 therefore tests only pages that never reach the model. It does not show that honest failure works on a page that was fetched and then judged unreadable.
- The grader prompts and the model are unchanged. No prompt was changed in this phase.

## Prompt versions (phase 3)
Each version changes one thing from the version before it. The run id and the version are logged in `runs.csv`; the eval loads `mnemo/save/prompts/<version>.txt`, so a run really uses that prompt.

| Version | One change from the version before | Save quality | Honesty | Folder choice | Tokens |
| --- | --- | --- | --- | --- | --- |
| save_v1 | Baseline prompt (no change). | 0.92 | 1.00 | n/a | 124480 / 128626 |
| save_v2 | Direct first sentence with an action verb: "Save one bookmark from the page text..." | 0.50 | 0.47 | 0.40 | 134575 |
| save_v3 | Added output rules as numbered steps. | 0.58 | 0.60 | 0.27 | 141693 |
| save_v4 | Wrapped the task, rules and steps in XML tags. The page text was already inside `<page>` tags. | 0.42 | 0.40 | 0.33 | 137991 |
| save_v5 | Added two readable examples and one unreadable-page example from the best outputs. | 0.92 | 0.93 | 0.73 | 143109 |

`save_v5` is the default in `mnemo/core/config.py`. It ties the baseline save quality (0.92), raises the folder choice from n/a to 0.73, and its honesty (0.93) is one page below the baseline, inside the 0.08 noise level. `save_v2` to `save_v4` lowered save quality and honesty, so they were rejected. The baseline rows predate the folder rule, so the folder choice is only compared between `save_v2` and `save_v5`.

## Rules
- Do not improve prompts in phase 2. Build the sets and graders first.
- Change one thing per run.
- Log every run, including bad ones.

Related: [definition of done](../process/definition-of-done.md), [phase 2 plan](../plans/phase-2-eval-harness.md).
