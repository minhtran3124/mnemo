# Test sets: how they work

Status: Draft v0.1 · Owner: KhoiTran · Phase: 2, 4, 7

This file explains the test sets (golden sets) used by the eval and where their files go.

## Purpose

The eval answers one question after each change: did the app get better or worse? Supports F-20. Sample links: [sample-links.md](../../reference/sample-links.md).

## Scope

In: set types, naming, held-out rule, who fills what.
Out: the eval scripts (`evals/graders.py`, `evals/run_eval.py`).

## The sets

| Set | Size | Used from | Doc |
| --- | --- | --- | --- |
| Save | 20 pages | Phase 2 | [save-golden-set.md](save-golden-set.md) |
| Ask | 15 questions plus 3 trick questions | Phase 4 | [ask-golden-set.md](ask-golden-set.md) |
| Route | 15 links | Phase 7 | [route-set.md](route-set.md) |
| Hard cases | 11 cases (not scored the same way) | Phase 1 on | [hard-cases.md](hard-cases.md) |

## Rules

| ID | Rule |
| --- | --- |
| TC-01 | Save every page text on disk. Each run uses the same input, not today's web. |
| TC-02 | Of the 20 Save pages, 5 are held-out. Never use them as prompt examples. They show whether a gain is real. |
| TC-03 | At least 2 of the 5 held-out pages are hard cases. |
| TC-04 | You write expected tags and key facts. Docs leave them blank: the owner fills them. |
| TC-05 | Do not change a target after you see results. |
| TC-06 | Run the baseline twice. The gap is the noise level. A later change must beat it. |
| TC-07 | After each run, read 3 results and the grader's reasons. If you disagree, fix the grader first. |

## Naming

| Thing | Name |
| --- | --- |
| Save page | `S-01` to `S-20` |
| Ask question | `A-01` to `A-15`, trick: `T-01` to `T-03` |
| Route link | `R-01` to `R-15` |
| Hard case | `H-01` to `H-11` |
| Page text file | `evals/golden/<id>.txt` |
| Run result | `evals/results/<run id>.csv` |

Held-out: mark with `held-out` in the notes column. Which 5: Open question.

## Scoreboard

Show three numbers side by side and never merge them: save quality, honesty, find rate.

## Open questions

- Which 5 are held-out.
- Pass targets (set after the first baseline).
