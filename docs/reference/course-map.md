# Course Map
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file shows which course lessons serve which feature. The course guide has 67 lessons. The map starts from the feature, not the lesson, so you do not add features only to tick a lesson.

## Feature to lessons

| Feature | Lessons | How it is built | Phase | Fit |
| --- | --- | --- | --- | --- |
| Quick save, honest failure | 1-8, 16-19 | Helpers, system prompt, low temperature, prefill plus stop sequence for clean JSON, direct and specific prompts, XML tags around the page text | 0, 1, 3 | Strong |
| Quality checks | 9-14 | Golden set, code grader, model grader, score table | 2 | Strong |
| Ask in plain words | 7, 20-28 | Search tool, tool loop, streamed answer | 4 | Strong |
| Screenshots | 40 | Image block in the save flow | 4 | Strong |
| Better search, Do I have this? | 32-38 | Chunking, BM25 over page text and over title, summary, tags and reason, merge with RRF, Claude picks the best 3 (no embeddings) | 5 | Strong |
| Sources, PDFs | 41, 42 | PDF as a document block, citations in answers | 6 | Strong |
| Folder proposals | 61-64, 67 | Router by link type, chain of steps, parallel sub-tasks, a model review step | 7 | Strong |
| Digest, roast | 5, 6, 39, 43-45 | Personality prompt, higher temperature for the roast, cache the long list, thinking only if the eval gains | 8 | OK |
| Use from Claude Code | 47-56, 60 | Bookmark store as an MCP server with tools, a resource and a prompt | 9 | OK |
| Dead-link doctor | 65, 66 | An agent that checks each result of its own actions | 10 | Optional |
| Report with a chart | 46 | Code execution and the Files API on a CSV | 10 | Optional |
| Replacement links | 31 | Web search tool with `allowed_domains` | 10 | Optional |
| Build the app | 58, 59 | Claude Code writes the code, you review | 0 | Strong |
| Online host | 1, 2 | Server holds the key; screens never do | A | Strong |
| None | 29, 30, 57 | Fine-grained tool calls, text editor tool, computer use | none | Weak |

## Coverage check
64 of the 67 lessons are used by at least one phase. Three are not used by any feature:

| Lesson | Topic | What to do |
| --- | --- | --- |
| 29 | Fine-grained tool calling (streaming tool arguments) | Read only. No screen needs it. |
| 30 | Text editor tool (Claude edits files) | Read only. A bookmark app has no file-editing job. Do not invent one. |
| 57 | Anthropic apps (overview of Claude Code and computer use) | Read with phase 9. It takes about 2 minutes. |

Four more lessons are used only in the optional phase 10:

| Lesson | Topic |
| --- | --- |
| 31 | Web search tool |
| 46 | Code execution and Files API |
| 65 | Agents and tools |
| 66 | Environment inspection |

If you cut phase 10, you lose all hands-on practice with a real agent. Phases 7 and 8 use workflows, which are not agents. If agents matter most to you, keep phase 10 and choose the dead-link doctor (see [phase 10 plan](../product/plans/phase-10-agent-optional.md)).

Lessons 34 to 36 (embeddings) are read only, because Mnemo does not use embeddings. See [embeddings alternatives](../research/embeddings-alternatives.md).

## Outside the course
These parts of the plan have no lesson. The time estimates for them are guesses, and you must test them yourself.

| Part | Phase | Why no lesson |
| --- | --- | --- |
| iPhone Shortcut | B | The course does not teach Shortcuts |
| .deb app | C | The course does not teach Linux packaging |
| Query rewrite and the "Claude picks" step | 5 | The plan's own design |
| Page fetching | 1 | Ask Claude Code to write a simple fetcher; use the GitHub API for repos |
| Web hosting | A | The course teaches the key rule, not hosting |

Related: [phases overview](../product/phases-overview.md), [roadmap](../product/roadmap.md).
