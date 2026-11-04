# Phase 10: Agent (Optional)
Status: Draft v0.1 · Owner: KhoiTran · Phase: 10

Optional phase: pick one of three small projects. If you cut it, you lose hands-on practice with a real agent (a program where Claude chooses actions in a loop).

## Goal
F-18 dead-link doctor, or one of two alternatives.

## You can now
Get fixes for dead links.

## Sessions and lessons
3 sessions. Lessons 31, 46, 65, 66.

## Inputs
Phase 4 done. Phase 8 helps (dead-link list).

## Tasks
Pick one choice and write it down first.
1. Choice A, dead-link doctor: tools `check_link`, `fetch_page`, `propose_fix`.
2. A: the agent writes proposals only. You approve each change.
3. A: after each action, the agent checks the result (lesson 66).
4. A: set a maximum number of steps.
5. Choice B, CSV chart: upload the log as CSV, ask for a chart with code execution and the Files API (lesson 46).
6. Choice C, replacement search: add the web search tool with `max_uses` and `allowed_domains` (lesson 31).
7. Run the chosen one on 5 dead or fake-dead links.

## Done when
- [ ] One choice works on 5 test cases.
- [ ] Nothing in `data/bookmarks.json` changes without your approval.
- [ ] The agent stops at its step limit.

## Risks
A wrong fix hurts your list. See [risk review](../../reviews/risk-review.md).

## If time runs short
Cut it first (first in cut order).

## Links to specs
[page reading](../../feature-specs/page-reading.md) · [digest and roast](../../feature-specs/digest-and-roast.md) · [roadmap](../roadmap.md)
