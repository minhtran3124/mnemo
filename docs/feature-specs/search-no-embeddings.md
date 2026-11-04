# Search without embeddings

Status: Draft v0.1 · Owner: KhoiTran · Phase: 5

This file describes the search design for D-006: no embeddings, because the project uses only the Claude API.

## Purpose

Find a bookmark when your words differ from the page words. Anthropic has no embedding API (lesson 34), so this is a design of ours. The query rewrite and the pick step are not in the course. See [embeddings-alternatives.md](../research/embeddings-alternatives.md).

## Scope

In: chunking, query rewrite, two indexes, merge, pick step, optional all-summaries option, eval, limits.
Out: embeddings (lessons 34 to 36 are read only).

## Requirements

| ID | Requirement |
| --- | --- |
| SE-01 | Page text is cut into chunks by size, with overlap (the common fallback when text has no fixed structure). |
| SE-02 | Before each search, Claude rewrites the question into keywords and similar words. |
| SE-03 | Two `BM25Index` objects (BM25 is a word-matching score): one over page chunks, one over title, summary, tags and reason. Same `add_document()` and `search()` methods. |
| SE-04 | A `Retriever` merges the two result lists with reciprocal rank fusion (RRF, a method that merges ranked lists). |
| SE-05 | The top 20 results go to Claude. Claude picks the best 3 and says why. |
| SE-06 | Search ignores folders (D-005). |
| SE-07 | Private bookmarks (proposed): only the second index (no page text exists to search). Open question. |

## Behavior and rules

```text
question -> rewrite -> BM25 (chunks)  \
                    -> BM25 (fields)   -> RRF -> top 20 -> Claude picks 3
```

Chunk size, overlap size and RRF constant: Open question. Tune with the eval.

### Optional: all summaries in one prompt

For a few hundred bookmarks, try sending all summaries in one prompt with a cache breakpoint (a mark that lets the API reuse the long part). Compare cost and find rate in the eval. Unverified: the minimum length for caching. Content below it is processed without caching and without an error, so read the cache fields in `usage`. Keep caching only if numbers show a gain.

### Eval comparison

The retrieval eval compares three setups on the Ask set:

| Setup |
| --- |
| BM25 alone |
| BM25 merged by RRF |
| Claude picking from the candidates |

If search is still weak, an embeddings provider can be added later.

## Limits

- Search is weaker for questions that use very different words from the page. The eval shows how much.
- Each search costs at least one extra Claude call (rewrite) and one for the pick.
- Few bookmarks make BM25 scores unstable. Open question.

## Edge cases

| Case | Behavior |
| --- | --- |
| Rewrite call fails | Use the original question. |
| Fewer than 20 candidates | Send all. |
| No candidate fits | Claude may answer "nothing found". |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | The retrieval eval prints a find-rate for the three setups. |
| 2 | Trick questions still return "nothing found". |
| 3 | A bookmark in the wrong folder is still found. |
| 4 | For caching: the two cache fields are read and written in the run log. |

## Tests

[ask-golden-set.md](test-cases/ask-golden-set.md). Duplicates also use this search ([duplicates.md](duplicates.md)).

## Open questions

- Chunk size, overlap, RRF constant.
- Whether the all-summaries option wins.
- Whether embeddings are needed later.
