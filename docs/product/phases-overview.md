# Phases Overview
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

One table of all phases, with links to each phase plan.

Visual page: [Roadmap](https://claude.ai/artifact/AJJLCpqJSUq927cvXRbBPx). It is a snapshot of `main` at commit `ce40e28` and is private until you share it. This file is the source of truth; if they differ, fix the page.

| Phase | Goal | Features | Sessions | Lessons | Done when | Depends on | Plan |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Safe, ready project | setup | 1 | 1-5, 58, 59 | Script gets an answer; second call remembers; key in `.env`, not git | none | [plan](plans/phase-0-setup.md) |
| 1 | Chat page and bookmark page | F-01 F-02 F-04 F-05 (Grid, List) | 3 | 3-8, 16, 17 | 5 public links give cards; unreadable page saved as link only | 0 | [plan](plans/phase-1-chat-and-bookmark-pages.md) |
| 2 | Eval harness | F-20 | 3 | 9-14 | One command scores 20 pages, prints 3 numbers; baseline run twice | 1 | [plan](plans/phase-2-eval-harness.md) |
| 3 | Trust and filing | F-01 F-03 F-05 (Compact) F-19 | 3 | 15-19 | 3+ prompt versions compared; Route set scores; Move and Undo work; 10 real saves | 2 | [plan](plans/phase-3-trust-and-filing.md) |
| 4 | Ask, import, screenshots | F-06 F-07 F-08 F-10 (screenshots) | 4 | 7, 20-28, 40 | 15 questions and 3 trick questions run; import in batches | 3 | [plan](plans/phase-4-ask-import-screenshots.md) |
| 5 | Search without embeddings | F-09 | 3 | 32-38 | Retrieval eval compares 3 methods; 5 planted duplicates caught | 4 | [plan](plans/phase-5-search-without-embeddings.md) |
| 6 | PDFs and quotes | F-08 F-10 (PDF) | 2 | 41, 42 | PDF saved; quote exists in page text | 4 | [plan](plans/phase-6-pdf-and-quotes.md) |
| 7 | Folder proposals | F-13 | 2 | 61-64, 67 | Accept/reject each folder; nothing moves without yes | 3, 5 | [plan](plans/phase-7-folder-proposals.md) |
| 8 | Digest and roast | F-14 F-15 | 3 | 5, 6, 39, 43-45 | Digest runs; roast numbers equal code counts | 4 | [plan](plans/phase-8-digest-and-roast.md) |
| 9 | MCP server | F-17 | 3 | 47-56, 60 (57 read here) | Inspector tests pass; Claude Code finds a bookmark | 4 | [plan](plans/phase-9-mcp-server.md) |
| 10 (optional) | One agent, chart or search | F-18 | 3 | 31, 46, 65, 66 | One of three choices works | 4 | [plan](plans/phase-10-agent-optional.md) |
| A | Online host | F-11 | 4 | 1, 2 | Online, login, spending cap; works on iPhone browser | 4 (and the 2-week test) | [plan](plans/phase-a-online-host.md) |
| B | iPhone Shortcut | F-12 | 1 | none | Share menu sends link; card appears | A | [plan](plans/phase-b-iphone-shortcut.md) |
| C (optional) | .deb window | F-16 | 2 | none | .deb installs and opens chat page | A | [plan](plans/phase-c-deb-app.md) |

Depends-on for phases 5 to 9 is a working assumption: the plan does not list it, so check it in [open questions](../research/open-questions.md). Phase 6 and 8 use the saved pages from phase 4.

## Dependency list
- 0 -> 1 -> 2 -> 3 -> 4 (strict chain).
- After 4: A and the 2-week test; then B (needs A).
- 5, 6, 8, 9, 10 need phase 4. 7 needs 3 and the eval.
- C needs A.

## Definition of ready to start the next phase
You may start a phase only when the previous phase "Done when" list passes. You run the checks yourself. If one fails, fix it or cut scope. Do not start the next phase. See [definition of done](../process/definition-of-done.md).
