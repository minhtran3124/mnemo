# Phase 2 follow-ups
Status: Draft v0.1 · Owner: KhoiTran · Phase: 2

Fix what the phase 2 review and the baseline left open, so phase 3 can compare prompt versions with a score that can fail.

## Goal
The eval harness reports an honesty score that can fail, and the faithful-summary grader is safe to trust, before any prompt is changed in phase 3.

## You can now
Trust a change in the three scores.

## Inputs
Phase 2 merged (PR #95, baseline PR #96). See the "Baseline and noise" section of [eval process](../../process/eval-process.md).

## Tasks
Each task is one change with its own check, so each can become one ticket.

1. **Honesty score that can fail.** In `evals/run_eval.py`, a page expected to be readable that is saved link only with a null summary, or a readable page the grader did not score, must not count as honest. Today it does, so a broken prompt or a missing golden file can read 1.00. Also add one unreadable fixture that reaches `save.preview` as short text (under the floor), so the honest-failure check runs on text that was fetched, not only on pages with no text. Check: new tests fail before the change and pass after.
2. **Grader prompt safety.** In `evals/faithful.py`, escape the page text and the summary before they go into the grader message, the same way `save._summarise` escapes `<page>`. Check: a test with a page text that contains a closing tag still sends one wrapper.
3. **Key-fact answers are checked.** In `evals/faithful.py`, a reply whose key-fact answers do not match the number of key facts counts as invalid output (retry once, then `grader_failed`), and `run_eval.py` prints how many key facts were found in each summary. Check: tests for a short list, a long list and the printed count.
4. **Text floor by source.** `save.preview` picks the text floor by host name with a magic string. Move the GitHub host rule to one named constant that `save.preview` and the fetcher share. Check: existing tests pass and a new test covers a `github.com` URL that is not a repository.
5. **Grader rules for hosting facts and index pages.** The grader marked "A GitHub repository" as unsupported on a repo README (S-06) and flipped on S-03 and S-09. Add two rules to `prompts/eval_faithful.txt`: a page's own kind (repository, index list) is supported by its address and layout; a claim about a listed item must appear in the list. Check: a prompt-content test and a documented before and after on S-03, S-06 and S-09.

## Not tickets (owner does these)
- Read the 15 draft answers in `evals/expected.json` and set `draft` to `false`.
- Send the full addresses of the six missing golden pages (rows 5, 6, 12, 13, 15 and 18 of [sample links](../../reference/sample-links.md)). A ticket can be written when they are known.

## Done when
- [ ] A run with a broken save prompt gives an honesty score below 1.00.
- [ ] The grader prompt cannot be closed early by page text.
- [ ] A reply with the wrong number of key-fact answers is treated as invalid.
- [ ] The GitHub host rule lives in one place.
- [ ] S-03, S-06 and S-09 are graded the same in two runs.

## Risks
The grader is a model, so Task 5 can reduce noise but not remove it. See [eval process](../../process/eval-process.md).

## Links to specs
[eval process](../../process/eval-process.md) · [save golden set](../../feature-specs/test-cases/save-golden-set.md) · [phase 2 plan](phase-2-eval-harness.md)
