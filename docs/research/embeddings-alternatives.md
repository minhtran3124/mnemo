# Embeddings Alternatives
Status: Draft v0.1 · Owner: KhoiTran · Phase: 5

This file explains why Mnemo has no embeddings, and what to do if search is weak.

An embedding is a list of numbers that stands for the meaning of a text. It lets a program find texts with similar meaning even when the words differ.

## Why no embeddings
- You chose to use only the Claude API (D-001).
- Anthropic has no embedding API (lesson 34).
- So phase 5 uses chunking, a query rewrite, two BM25 indexes, RRF, and Claude picking the best 3 (D-006).
- Lessons 34 to 36 are read only. Do not build them.

## The cost of this choice
Search will be weaker for questions that use very different words from the page. The phase 5 eval shows how much weaker. The query rewrite step (Claude adds keywords and similar words) is meant to reduce this gap. It is the plan's own design, not in the course.

## What to try before adding anything
1. Check the failures in the retrieval eval. Are they questions with very different words?
2. Improve the query rewrite prompt, one change at a time.
3. For a few hundred bookmarks, send all summaries in one prompt with a cache breakpoint and compare cost and find rate. Unverified: the caching minimum (see [API notes](../reference/api-notes.md)).
4. Improve what the second index holds (title, summary, tags and reason).

## If the phase 5 eval is still weak
Decide with numbers from the eval, not with feeling.

| Situation | Action |
| --- | --- |
| Find rate meets the target you set after the first baseline | Do nothing |
| Find rate is below target, and the misses are word-mismatch cases | Consider an embeddings provider later |
| Find rate is low for other reasons (bad page text, unreadable pages) | Fix those first; embeddings will not help |

## Provider option later
The plan says an embeddings provider can be added later. It names none. Open question: which provider, its price, and its data policy. Do not choose one without checking those. Adding a second provider changes decision D-001 and the privacy picture (more text leaves your machine). Record a new decision in the [decision log](../process/decision-log.md) first.

## Course note
Read lessons 34 to 36 so you understand the idea. See the [course map](../reference/course-map.md).

Related: [search spec](../feature-specs/search-no-embeddings.md), [phase 5 plan](../product/plans/phase-5-search-without-embeddings.md).
