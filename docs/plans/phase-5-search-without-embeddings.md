# Phase 5: Search Without Embeddings
Status: Draft v0.1 · Owner: KhoiTran · Phase: 5

Find links when your words differ from the page, using only the Claude API (D-006). Add the duplicate warning.

## Goal
Better search and F-09.

## You can now
Find with different words, and get a duplicate warning.

## Sessions and lessons
3 sessions. Lessons 32-38 (34 to 36 are read only).

## Inputs
Phase 4 done and the 2-week test result. The ask eval from phase 4 as baseline. 5 planted duplicates.

## Tasks
1. Chunk page text by size with overlap.
2. Write `BM25Index` with `add_document()` and `search()`.
3. Build two indexes: one over page chunks, one over title, summary, tags and reason.
4. Add query rewrite: Claude turns the question into keywords and similar words. This is not in the course.
5. Merge the two result lists with reciprocal rank fusion in a `Retriever`.
6. Send the top 20 to Claude; it picks the best 3 and says why.
7. Eval: compare BM25 alone, BM25 with RRF, and Claude picking. Record find rate and cost.
8. Optional test: all summaries in one prompt with a cache breakpoint. Read cache fields. Keep it only if numbers gain.
9. Duplicate check on save: same cleaned URL is "saved already"; a candidate Claude calls the same page is "saved something similar". See [duplicates](../feature-specs/duplicates.md).
10. Test 5 planted duplicates, including the Brotli near-duplicate pair and the `fbclid` repeat.

## Done when
- [ ] Retrieval eval table compares the three methods.
- [ ] The best method is chosen from numbers, not feeling.
- [ ] All 5 planted duplicates are caught with the right message.
- [ ] Trick questions still return "nothing found".
- [ ] If search is weak, you wrote an open question about adding embeddings later ([alternatives](../research/embeddings-alternatives.md)).

## Risks
Weaker search for very different words; caching may not help (minimum length Unverified). See [risk review](../research/risk-review.md).

## If time runs short
Skip the cache test. Keep RRF and the duplicate check. Phase 5 can be cut after the 2-week test if the page already solves your problem.

## Links to specs
[search without embeddings](../feature-specs/search-no-embeddings.md) · [duplicates](../feature-specs/duplicates.md) · [ask and answers](../feature-specs/ask-and-answers.md) · [ask golden set](../testing/golden-sets/ask-golden-set.md)
