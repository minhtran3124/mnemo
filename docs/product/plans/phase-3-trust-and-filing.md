# Phase 3: Trust and Filing
Status: Draft v0.1 · Owner: KhoiTran · Phase: 3

Improve the cards with the eval, add safe auto-filing, Compact view and private mode.

## Goal
F-01 (reason test), F-03 (filing with Move and Undo), F-05 (Compact), F-19 (private mode, proposed).

## You can now
Trust the cards and the filing.

## Sessions and lessons
3 sessions. Lessons 15-19.

## Inputs
Phase 2 done with a baseline. You wrote 5-6 starter folders (open question; "Unsorted" always exists). The Route set of 15 links with expected types: [route set](../../feature-specs/test-cases/route-set.md).

## Tasks
1. Change one thing per run and log it: direct first sentence with an action verb.
2. Add output rules and numbered steps. Run the eval.
3. Add XML tags. Run the eval.
4. Add 2-3 examples from your best outputs, including one unreadable page. Run the eval. Keep at least 3 compared versions.
5. Write the starter folders in `config.py`.
6. Filing step: return one existing folder or Unsorted when unsure. Code rejects unknown folders (D-005). Search ignores folders.
7. Show "Filed in: ..." on the card with Move and Undo always visible. See [safe auto-filing](../../solutions/safe-auto-filing.md).
8. Score the folder choice on the Route set.
9. Add the Compact view (F-05). Keep Grid and List working.
10. Add private mode F-19: a link marked private is saved as link only and nothing is sent to the API. Add the proposed field `private`.
11. Make `reason_source` visible: "guess" label on guessed reasons.
12. Reason test: save only real links for one week. Count how often you type a reason. This is decision point 1.
13. Try 10 real saves. Check each folder choice.

## Done when
- [ ] At least 3 prompt versions compared, one change at a time.
- [ ] Route set scored; unsure links go to Unsorted.
- [ ] A made-up folder name is rejected by code (test it).
- [ ] Move and Undo work on 10 real saves.
- [ ] Compact view works.
- [ ] A private link makes no API call (check `data/log.jsonl` and your Console usage).
- [ ] You wrote down whether you type the reason.

## Risks
The reason field stays empty; wrong folder hides a bookmark. See [risk review](../../reviews/risk-review.md).

## If time runs short
Cut Compact view. Keep filing rules, Move, Undo and private mode.

## Links to specs
[classification and filing](../../feature-specs/classification-and-filing.md) · [folders](../../feature-specs/folders.md) · [bookmark page and views](../../feature-specs/bookmark-page-and-views.md) · [privacy and security](../../feature-specs/privacy-and-security.md) · [data model](../../feature-specs/data-model.md) · [route set](../../feature-specs/test-cases/route-set.md) · [save golden set](../../feature-specs/test-cases/save-golden-set.md)
