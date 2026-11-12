# Graph (an index for AI agents)

Status: Draft v0.1 · Owner: KhoiTran · Phase: not planned yet (Open question)

This file describes the graph: a map of everything you saved and how the items connect. Its first user is an AI agent that must find things fast to answer a question. The picture for a human comes second.

Nothing in this file is built in the app. A picture of a graph exists only in the [hub prototype](https://claude.ai/artifact/77KLF6DA2WFCMescbP92Vf), on sample data. The graph has no F id in the [PRD](../product/mnemo-prd.md) and no phase plan. Both are Open questions below.

## Purpose

An agent asks "what do I already know about X?" or "what is connected to this item?". Reading every saved item for each question is slow and costs money. The graph gives the agent a short list of the right items first, with the reason each one is there. The agent then reads only those.

Decided by the owner in the project chat:

- The graph serves AI agents first.
- Links come from tags and other plain rules. No embeddings (D-001, D-006).
- Every kind of item the app can save goes in the graph.

## Scope

In: nodes, links, link reasons, the questions an agent can ask, how the graph stays in sync, the human view (later).
Out: word search ([search-no-embeddings.md](search-no-embeddings.md)), how an agent connects to the app ([mcp-server.md](mcp-server.md)), the record itself ([data-model.md](data-model.md)).

## Words

- **Node**: one point in the graph. An **item node** is one saved thing. A **topic node** is one tag.
- **Link**: a line between two nodes. Every link has a **kind** and a **reason**.
- **Thin node**: an item with no summary or no tags. The app knows little about it.

## Requirements

| ID | Requirement |
| --- | --- |
| GR-01 | Every saved item is one item node: id, type, title, summary, tags, folder, date saved. |
| GR-02 | Every tag is one topic node. |
| GR-03 | The graph accepts any item type. Today only bookmarks exist, so only bookmarks appear. A new type (note, file, video, task) must need no change to the graph rules. |
| GR-04 | Links are made by plain code, never by Claude and never by embeddings. The kinds are in the table below. |
| GR-05 | Every link stores its kind and a reason in plain words, for example "both have the tag testing". |
| GR-06 | The graph is an index, not a second store. It is built from the records that `mnemo/core/store.py` returns. It can be deleted and rebuilt at any time with no loss (proposed, D-039). |
| GR-07 | The graph changes when an item is added, edited or deleted. It never shows a deleted item. |
| GR-08 | An agent can only read the graph. It cannot add, change or remove nodes or links through it. |
| GR-09 | A thin node is marked as thin in every answer. A node with a null summary stays null. The graph never writes a summary (NF-04, [honest failure](../solutions/honest-failure.md)). |
| GR-10 | Every answer points to the original item (its id), so the agent or you can open it. |
| GR-11 | An agent reaches the graph through the web server's HTTP API, like every other reader (D-022). |
| GR-12 | Building or reading the graph makes no Claude call. It costs no API money. |

## Link kinds

All are found by code from fields the record already has.

| Kind | Two nodes are linked when | Strength | Status |
| --- | --- | --- | --- |
| `tag` | An item has a tag (item to topic). | Strong | In the prototype |
| `site` | Two items come from the same website (same host in `url_clean`). | Medium | Proposed |
| `folder` | Two items are in the same folder. `Unsorted` does not count. | Medium | Proposed |
| `mention` | The page text of one item holds the link of another saved item. | Strong | Proposed |
| `session` | Two items were saved close together in time. | Weak | Proposed. Open question: what "close" means, and whether this link is noise. |

Strength is used to rank answers. The numbers behind Strong, Medium and Weak are an Open question. Tune them with an eval.

## What an agent can ask

| Question | Answer |
| --- | --- |
| "Find items about X." | Item nodes linked to topic X, ranked by how many links and how strong. Each with its reasons. |
| "What is connected to item N?" | Its neighbours, one step out. Two steps on request. Each with the link kind and reason. |
| "Which topics exist?" | All topic nodes with a count of items. |
| "Give me item N." | The node fields. The full record comes from the normal bookmark endpoint. |

Rules:

- An answer has a size limit, so it stays small for the agent. The limit is an Open question.
- X must match a tag. If no tag matches, the answer is "nothing found", and the agent should use word search instead ([search-no-embeddings.md](search-no-embeddings.md)). The graph does not guess.
- Search finds items by words. The graph finds items by links. An agent can use search first, then ask the graph for the neighbours of the result. Whether the app merges the two lists itself is an Open question.

## The human view (later)

The prototype shows these. None is built in the app. They come after the agent part.

1. A Graph screen in the menu, with a count of items, topics and links.
2. Items as circles, topics as diamonds, lines between them.
3. A note that links are made by the app and can be wrong.
4. Click a node: its links get bright, a side panel lists "Connected to".
5. A plain list of all nodes, for keyboard use.
6. Open an item in the reader from the panel.
7. "Show in graph" and a "Related" list on an item page.

Not in the prototype, wanted later: zoom and pan, filter by type or tag, a layout that works with hundreds of nodes, a phone view, hiding a wrong link. The V3 design has no Graph board, so a design is needed first ([ui-reference.md](ui-reference.md)).

## Limits

- The graph is only as good as the tags. Claude writes the tags at save time. Two items about one subject with different tags are not linked by `tag`. The other link kinds reduce this but do not remove it.
- Links by meaning are not possible without embeddings (D-001, D-006).
- A thin node has few links, so the agent will rarely find it through the graph.
- Unverified: how large the graph can get before building it on each change is too slow.

## Edge cases

| Case | Behavior |
| --- | --- |
| No items | Empty graph. Answers are "nothing found". |
| Item with no tags | It is a node. It can still have `site`, `folder`, `mention` or `session` links. Marked thin. |
| Item deleted | Its node and its links go. A topic with no items left goes too. |
| Tag edited | Old links go, new links appear. |
| Item id not found | Clear error. |
| Private item (F-19) | Open question, the same one as for search and the MCP server. |
| Two tags that differ only by case or spaces | Open question: treat as one topic or two. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | After a save, the new item is a node and has a `tag` link for each of its tags. |
| 2 | After a delete, no answer holds that item. |
| 3 | Deleting the graph and building it again gives the same nodes and links. |
| 4 | Every link in an answer has a kind and a reason. |
| 5 | A thin node is marked thin, and its summary is still null. |
| 6 | Building and reading the graph make no Claude call (checked in a test with no API key). |
| 7 | No endpoint of the graph changes a record. |
| 8 | A question about a tag that does not exist returns "nothing found". |

## Tests

Not written. A small fixed set of bookmarks with known tags, sites and folders is enough to check every link kind by hand first. An eval that compares "search alone" with "search plus graph" on the [Ask golden set](../testing/golden-sets/ask-golden-set.md) would show whether the graph helps. Open question.

## Open questions

- Which phase. Proposed: after phase 5 (search) and before or inside phase 9 (MCP server), because the agent reaches the graph through the same door.
- A feature id in the PRD (F-21?) and a place in the roadmap.
- Whether private items appear.
- Link strengths, the answer size limit and the meaning of "close in time".
- Whether the `session` link is useful or noise.
- Whether the app merges search results and graph results.
- Whether the graph is kept in a file or built in memory at start.
- Notes, files, videos and tasks have no spec yet, so GR-03 cannot be tested with them.
- A V3 design for the human view.
