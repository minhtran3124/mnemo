# Phase 8: Digest and Roast
Status: Draft v0.1 · Owner: KhoiTran · Phase: 8

Give something back every week (product rule 4).

## Goal
F-14 weekly digest and F-15 roast.

## You can now
Get the weekly digest and the roast.

## Sessions and lessons
3 sessions. Lessons 5, 6, 39, 43-45.

## Inputs
Phase 4 done. `open <id>` logging works. A list with some never-opened bookmarks.

## Tasks
1. Code picks digest candidates: never opened, oldest first, close to your recent questions.
2. Claude writes only the "why now" line for each of 3 items.
3. Code finds near-duplicates (reuse phase 5 if built) and dead links.
4. Roast: code counts the numbers; a personality system prompt and higher temperature write the words around them.
5. Code check: every number in the roast equals the code's count.
6. Add a cache breakpoint to the long list. Read `cache_creation_input_tokens` and `cache_read_input_tokens`. Keep caching only if numbers show a gain (minimum length Unverified).
7. Try extended thinking on `folders`. Keep or drop by the eval.
8. Log digest opens in `data/log.jsonl` for the "Do I come back?" measure.

## Done when
- [ ] Digest runs on your list: 3 reads, duplicates, dead links.
- [ ] Every roast number equals the code count.
- [ ] You read both cache fields and wrote the decision.
- [ ] Thinking is kept or dropped based on the eval.

## Risks
Roast invents a number; caching does not help. See [risk review](../research/risk-review.md).

## If time runs short
Cut caching and thinking (third in cut order). Keep digest and roast.

## Links to specs
[digest and roast](../feature-specs/digest-and-roast.md) · [duplicates](../feature-specs/duplicates.md) · [storage](../feature-specs/storage.md) · [eval process](../testing/eval-process.md)
