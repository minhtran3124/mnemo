# Phase 2: Eval Harness
Status: Draft v0.1 · Owner: KhoiTran · Phase: 2

Build a way to measure quality, so you can tell if a change helps. F-20 is an internal tool.

## Goal
One command scores 20 saved pages and prints three numbers: save quality, honesty and find rate (find rate stays empty until phase 4).

## You can now
See whether a change helps.

## Sessions and lessons
3 sessions. Lessons 9-14.

## Inputs
Phase 1 done. 20 links chosen (include the PDF, Slack link, YouTube video, failed fetch, repeat link, index page; at least 2 of the 5 hidden links are hard cases). See [save golden set](../../feature-specs/test-cases/save-golden-set.md).

## Tasks
1. Save the text of 20 pages to `evals/golden/`, so each run uses the same input.
2. For each page, write the expected type, 3-6 expected tags and 2-4 key facts.
3. Mark 5 pages as held-out. Never use them as prompt examples.
4. Write code checks in `graders.py`: valid JSON and schema, tag rules (3-6 lowercase), summary at most 60 words, honest failure (unreadable gives null summary), type match, tag overlap.
5. Write the model grader for faithful summary: list statements the page does not support; the count must be 0; yes or no per key fact. Include the screenshot "claim not in image" check as a rule.
6. Write `run_eval.py` and the run log: one CSV row in `evals/results/` per run (run id, prompt version, model, three scores, tokens).
7. Show three scores side by side. Do not merge them into one average.
8. Run the baseline twice. The gap is your noise level.
9. Read 3 results and the grader's reasons. Fix the grader first if you disagree.
10. Write down what you changed in the [session log](../../process/session-log-template.md). Do not improve any prompt in this phase.

## Done when
- [ ] One command scores the 20 pages and prints three numbers.
- [ ] The baseline ran twice and the noise level is written down.
- [ ] You read 3 results and the grader's reasons.
- [ ] The unreadable page gets a null summary and passes the honest check.
- [ ] The CSV has one row per run.

## Risks
The eval is subjective and the grader is a model. See [eval process](../../process/eval-process.md).

## If time runs short
Keep the code checks and the faithful-summary grader. Cut tag overlap.

## Links to specs
[save golden set](../../feature-specs/test-cases/save-golden-set.md) · [hard cases](../../feature-specs/test-cases/hard-cases.md) · [test cases README](../../feature-specs/test-cases/README.md) · [test strategy](../../manual-testing/test-strategy.md)
