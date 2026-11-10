# Phase 7: Folder Proposals
Status: Draft v0.1 · Owner: KhoiTran · Phase: 7

Let Claude propose a folder structure for the whole list. You decide.

## Goal
F-13. Compare four ways to build the save step.

## You can now
Let Claude propose new folders.

## Sessions and lessons
2 sessions. Lessons 61-64, 67.

## Inputs
Phase 3 (filing and Route set) done. Enough saved bookmarks to need folders (an imported pile helps).

## Tasks
1. Build a router that picks the pipeline by link type (Route set of 15 links).
2. Build four versions of the save step: single prompt; chain (extract key facts, summarize, tag, suggest folder); parallel sub-tasks merged in code; review step. Run the same eval on each and write a comparison table.
3. Add a `folders` tool that proposes new folders for the whole list.
4. Show each proposal with accept, change, reject. Nothing moves without your yes (product rule 3).
5. Code check: every bookmark has exactly one folder after accept.
6. Try extended thinking on `folders` only, in phase 8 if time allows.
7. Consider the proposed types `docs` and `other` (D-013, not yet built). Decide with the eval.

## Done when
- [ ] Table compares single prompt, chain, parallel and review step.
- [ ] You accept or reject each proposed folder.
- [ ] No bookmark moves before you accept.
- [ ] Every bookmark has exactly one folder.
- [ ] Undo still works.

## Risks
An agent or tool changes your data. Proposals only. See [risk review](../research/risk-review.md).

## If time runs short
Cut the router and parallel parts (fourth in cut order). Keep the `folders` tool.

## Links to specs
[folders](../feature-specs/folders.md) · [classification and filing](../feature-specs/classification-and-filing.md) · [route set](../testing/golden-sets/route-set.md) · [safe auto-filing](../solutions/safe-auto-filing.md)
