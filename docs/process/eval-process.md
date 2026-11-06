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

The set files are in `evals/golden/`. See [test cases](../feature-specs/test-cases/README.md) for content.

## Held-out set
Keep 5 of the 20 save pages as a held-out set. Never use them as prompt examples. If a score rises on the other 15 but not on these 5, the gain may not be real. At least 2 of the 5 should be hard cases. `run_eval.py` prints the save quality of the held-out pages and of the tuning pages on separate lines; compare them after each run. runs.csv keeps the pooled figure.

## Baseline twice
Run the first version of the prompt two times. The gap between the two runs is your noise level. A later change must beat that gap, or you cannot say it helped.

## Noise rule
Keep a change only if the score rises by more than the noise. If it does not, undo the change.

## Three separate scores
Show three numbers side by side. Do not average them. An average can hide a drop in honesty.

| Score | What it covers |
| --- | --- |
| Save quality | Valid JSON, 3 to 6 lowercase tags, summary at most 60 words, type match, tag overlap |
| Honesty | The share of all pages that are honest: an unreadable page gives a null summary, or a readable page is scored by the faithful-summary grader with zero unsupported statements. A readable page saved link only, with a null summary, is not honest, because it was not graded. A readable page whose grader failed or errored is not honest: it counts in the denominator and is named in `notes`, so grader failures lower honesty. If the grader scored fewer than half of the readable pages it was asked to grade, honesty is left blank and `notes` says so, so a grader outage cannot read as 1.00 |
| Find rate | Right bookmark in the top 3; trick questions return nothing |

## Graders
A grader is code or a model that scores an output.
- Code graders are exact: schema, tag rules, summary length, null summary on failure, type match, tag overlap, every cited bookmark number exists.
- A model grader reads the page text and the summary, lists each statement the page does not support, and says yes or no for each key fact. The model grader can be capricious (lesson 13). The yes or no design is a plan choice, not a course rule.

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
| model | The model name from `config.py` |
| save_quality | Score 1: share of readable pages that pass the code checks |
| honesty | Score 2: the share of all pages in `evals/pages.json` that are honest (unreadable pages with a null summary, plus readable pages scored with zero unsupported statements). The run prints the split into unreadable and readable pages. The count of readable pages with zero unsupported statements is also written to `notes`. |
| find_rate | Score 3. Empty until phase 4 |
| tokens_used | Total tokens for the run: the save calls plus the grader calls |
| notes | `0 unsupported: N`, the count of scored readable pages with zero unsupported statements, then pages the faithful grader could not score, for example `0 unsupported: 9; not scored: S-03`. Pages the grader could not score count as not honest. A readable page saved link only with a null summary has no statements to grade, is not honest, and is not listed. |

Open question: whether to add a cost column. The plan lists only the columns above.

## Baseline and noise
The unchanged save prompt (`save_v1`, model `claude-haiku-5-5`) ran twice on the 15 golden pages. 12 are readable and 3 are unreadable (S-08, S-10 and S-15). Every expected answer is still a draft.

| Run | Save quality | Mean tag overlap | Honesty (unreadable pages honest) | Pages with 0 unsupported statements | Tokens |
| --- | --- | --- | --- | --- | --- |
| baseline-1 | 0.92 (11/12) | 0.40 | 1.00 (3/3) | 11 of 12 | 124480 |
| baseline-2 | 0.92 (11/12) | 0.33 | 1.00 (3/3) | 10 of 12 | 128626 |
| Gap | 0.00 | 0.07 | 0.00 | 1 page (0.08) | 4146 |

Both baseline rows were scored under the old honesty rule (the share of unreadable pages that are honest), so their honesty of 1.00 is not comparable with a run under the new rule. The rows are not edited.

Noise level: 0.08 (the faithful-summary count moved by 1 page of 12; save quality and honesty did not move, mean tag overlap moved by 0.07).

**Unverified:** these gaps and the noise level were measured under the old honesty rule, so they are not yet a valid bar for a later change under the new rule. Do not use them to judge an improvement until the baseline is re-run under the new rule (a later ticket; the committed rows stay as they are).

Read 3 results with the grader's reasons (S-03, S-06 and S-09, the pages the grader failed):
- S-03 (Airtable home): failed with 2 unsupported statements in baseline-2, passed in baseline-1, and passed with 0 when graded again for this note. The grader is not stable on this page. This is the main source of the faithful-summary gap.
- S-06 (ai_agents_az repo): failed with 1 unsupported statement in baseline-1: the summary says "A GitHub repository", and the grader said the page never says it is hosted on GitHub. The page is a repo README, so this is a grader false positive. Not fixed in this phase.
- S-09 (wearedevelopers videos): failed with 3 unsupported statements in baseline-2 and passed in baseline-1 and when graded again. The summary is an index list; the grader's strictness varies from run to run.

Limits of these numbers:
- The expected tags, types and key facts are Claude-written drafts and have not been reviewed, so tag overlap (0.33 to 0.40) and type match say little yet.
- S-08 (YouTube) and S-10 (Airtable developers) failed the live fetch, so they have no text and count as unreadable. Under the old rule the honesty score of 1.00 therefore tested only pages that never reach the model. It does not show that honest failure works on a page that was fetched and then judged unreadable.
- The grader prompts and the model are unchanged. No prompt was changed in this phase.

## Rules
- Do not improve prompts in phase 2. Build the sets and graders first.
- Change one thing per run.
- Log every run, including bad ones.

Related: [definition of done](definition-of-done.md), [phase 2 plan](../product/plans/phase-2-eval-harness.md).
