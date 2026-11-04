# Glossary
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file explains the words used in the Mnemo docs in plain English.

| Term | Meaning |
| --- | --- |
| API | A way for one program to ask another program to do work. Mnemo calls the Claude API. |
| API key | A secret string that proves a program may use your account. It also spends your money. Keep it in `.env`. |
| Agent | A program where the model decides which steps and tools to use, and checks the result of each action. Phase 10 is the only agent in the plan. |
| Workflow | A fixed path of steps that you design. Phases 7 and 8 use workflows. The course says to prefer them over agents. |
| Token | A small piece of text that the model counts. You pay by tokens. |
| `max_tokens` | A limit on how long the model's answer can be. It controls cost (NF-02). |
| Prompt | The text you send to the model. |
| System prompt | Standing instructions that tell the model its role and rules. |
| Temperature | A setting for how random the answer is. Low means steady. High means more varied. The roast uses a higher value. |
| Prefill | Starting the model's answer for it, so it continues in a set form (for example JSON). Unverified: which models support it. |
| Stop sequence | A piece of text that makes the model stop. Used with prefill for clean JSON. |
| JSON | A text format for structured data. Bookmarks are saved as JSON. |
| Schema | The list of fields and allowed values a record must have. |
| XML tags | Labels like `<page>` around text, so the model can tell the page text from your instructions. |
| Golden set | A fixed list of inputs with the answers you expect, used to test quality. |
| Eval | A repeatable test that gives a score. Short for evaluation. |
| Grader | Code or a model that scores one output. |
| Baseline | The score of the first version. Later versions are compared to it. |
| Noise | The gap between two runs of the same version. A change must beat it. |
| Held-out set | Test items you never use as prompt examples. |
| Faithful summary | A summary that contains only facts found in the page. |
| Honest failure | When a page cannot be read, the app says so and writes no summary (F-02). |
| Hallucination | A made-up fact from a model. Not used as a formal term in the plan; the plan says "invented fact". |
| Chunk | A piece of page text, cut by size with some overlap. Search works on chunks. |
| BM25 | A classic search method that ranks text by matching words. No model needed. |
| RRF | Reciprocal rank fusion. A way to merge two ranked lists into one. |
| Embedding | A list of numbers that stands for the meaning of text. Mnemo does not use them (D-006). |
| Query rewrite | Claude changes your question into keywords and similar words before search. |
| RAG | Retrieval-augmented generation. Find relevant text first, then ask the model to answer from it. |
| Retrieval | Finding the right items from your list. |
| Top 3 | The three best results shown. Mnemo never shows more than three. |
| Tool use | The model asks your code to run a function, then reads the result. |
| Tool loop | Keep running while `stop_reason` is `tool_use`; answer every tool call. |
| `is_error` | A flag you send back when a tool failed. |
| Streaming | Showing the answer as it is written. |
| MCP | Model Context Protocol. A standard way to give tools and data to a model app such as Claude Code. Phase 9. |
| MCP Inspector | A tool for testing an MCP server by hand. |
| Cache breakpoint | A mark that tells the API to reuse a long, unchanged part of the prompt. |
| Prompt caching | Reusing the start of a prompt to save cost. Unverified: the minimum length. |
| Extended thinking | The model reasons longer before answering. Kept only if the eval gains. |
| Citation | A pointer from an answer to the text it used. Phase 6. |
| Near-duplicate | Two different links about the same content, for example two news sites on one story. |
| Exact duplicate | The same link after tracking parts are removed. |
| Tracking part | Extra text in a link, such as `fbclid` or `utm_*`, that does not change the page. |
| `og:image` | A page's own preview image, named in the page head. Proposed for covers. |
| Router | A step that picks which pipeline to use, for example by link type. |
| Unsorted | The folder that always exists. Unsure links go there (D-005). |
| Move / Undo | Buttons on every filed card that change or reverse the folder. |
| Private mode | Proposed (F-19): a private link is saved as link only and nothing is sent to the API. |
| `store.py` | The one file through which all bookmark reading and writing goes (NF-03). |
| `.env` | A local file that holds secrets. Never committed. |
| `127.0.0.1` | Your own computer's address. A server bound to it cannot be reached from other devices. |
| `0.0.0.0` | An address that means "all networks". Binding to it can expose your server. Avoid it. |
| Shortcut | An iPhone automation that can appear in the Share menu. |
| Render | The host the plan expects to use in phase A. Price and storage unverified. |
| Smoke test | A quick check that main paths still work. |
| Acceptance criteria | Checks that say a feature is finished. |
| ADR | Architecture decision record. See the [decision log](../process/decision-log.md). |

See also: [course map](course-map.md), [API notes](api-notes.md).
