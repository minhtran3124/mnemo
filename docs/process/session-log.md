# Session log

## Session (unnumbered) · Phase 2

**Goal:** run the eval baseline twice and write down the noise level.
**Done:** `baseline-1` and `baseline-2` ran on the unchanged `save_v1` prompt over the 15 golden pages. Noise level is 0.08, written in `docs/testing/eval-process.md`. I read the grader's reasons for S-03, S-06 and S-09.
**Checked by:** eval (`uv run python -m evals.run_eval`), twice, plus `tests/test_eval_baseline.py`.
**Not done or broken:** the expected answers are still drafts (not reviewed). Six golden pages are missing (rows 5, 6, 12, 13, 15 and 18 of the sample links have no full address). S-08 and S-10 failed the live fetch and count as unreadable. The faithful-summary grader flips between runs on S-03 and S-09, and gives a false positive on S-06.
**Decisions:** none. No prompt or grader was changed.
**Open questions:** whether the model grader needs a looser rule for hosting facts and index pages before the next prompt change.
**Cost note:** about 125k tokens per run, 2 runs, plus 3 grader reads.
**Next task:** review the draft expected answers (set `draft` to false), then add the six missing golden pages.
