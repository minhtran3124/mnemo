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
| Honesty | Unreadable page gives a null summary; faithful-summary grader lists zero unsupported statements |
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
| honesty | Score 2: one number, the share of checked pages that are honest. Checked pages are the unreadable pages (null summary) plus the readable pages the faithful grader scored (zero unsupported statements). The run prints the split. |
| find_rate | Score 3. Empty until phase 4 |
| tokens_used | Total tokens for the run: the save calls plus the grader calls |
| notes | Pages the faithful grader could not score, for example `not scored: S-03`. They count as failures in the honesty score. |

Open question: whether to add a cost column. The plan lists only the columns above.

## Rules
- Do not improve prompts in phase 2. Build the sets and graders first.
- Change one thing per run.
- Log every run, including bad ones.

Related: [definition of done](definition-of-done.md), [phase 2 plan](../product/plans/phase-2-eval-harness.md).
