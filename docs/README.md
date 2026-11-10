# Mnemo docs

Status: Draft v0.1 · Owner: KhoiTran · Phase: all

Mnemo is a personal AI bookmark app. You paste a link in a chat. The app reads the page, writes a short summary, picks a folder and saves it. You find things again by asking in your own words. It uses the Claude API only. These docs hold everything we decided before the first line of code.

The name was chosen by you. Other software already uses "mnemo" (see [naming](research/naming.md)). That is fine for a personal project. Check again before any public release.

## Start here

1. [Pre-start checklist](process/pre-start-checklist.md): what must be true before phase 0.
2. [PRD](product/mnemo-prd.md): what we build and why.
3. [Roadmap](product/roadmap.md) and [phases overview](product/phases-overview.md): in what order.
4. [Open questions](research/open-questions.md): what you still need to answer. None blocks phase 0.

## Visual pages

Four pages draw these docs as pictures. They are snapshots of `main` at commit `ce40e28`. They are private until you share them. The docs are the source of truth; if a page and a doc differ, fix the page.

| Page | Shows | Linked from |
| --- | --- | --- |
| [Roadmap](https://claude.ai/artifact/AJJLCpqJSUq927cvXRbBPx) | Phases, releases, sessions, decision points, what to cut | [roadmap](product/roadmap.md), [phases overview](product/phases-overview.md) |
| [User workflow](https://claude.ai/artifact/PH6PBSCNxy76aeVVijwsgQ) | How you save, find, file and ask; who decides each step | [PRD](product/mnemo-prd.md), [chat and intent](feature-specs/chat-and-intent.md) |
| [Architecture](https://claude.ai/artifact/HRJ54QxYXpooHoemp6uSgV) | Pages, server, `mnemo/core/store.py`, Claude API, MCP; trust boundary; all decisions | [tech stack](product/tech-stack.md), [server API](feature-specs/server-api.md), [privacy](feature-specs/privacy-and-security.md) |
| [Data model](https://claude.ai/artifact/RjucLkUNCY5pWzD3RxJkpt) | Records, fields, files, bookmark lifecycle | [data model](feature-specs/data-model.md), [storage](feature-specs/storage.md) |

The design mockup (V3, light and dark) is linked from [frontend UI](feature-specs/frontend-ui.md). Its source is saved in [design/v3-mockup](design/v3-mockup/README.md), and [UI reference](feature-specs/ui-reference.md) says how the build must follow it.

Building these pages found conflicts between docs. They are settled under [Conflicts between docs](#conflicts-between-docs).

## Folder map

Each folder answers one question. A new doc goes in the folder whose question it answers.

| Folder | Purpose (one line) |
| --- | --- |
| [`product/`](product/) | What we build and why: PRD, roadmap, phases overview, tech stack. |
| [`plans/`](plans/) | What we do next: one plan per phase (0 to 10, A, B, C). |
| [`feature-specs/`](feature-specs/) | What each feature must do: one spec per feature area. |
| [`testing/`](testing/) | How we check the app: test strategy, manual checks, eval process. [`golden-sets/`](testing/golden-sets/) has the golden sets and hard cases. |
| [`process/`](process/) | How we work and the running record: agreements, definition of done, secrets, pre-start checklist, decision log, session log. |
| [`reference/`](reference/) | Facts to look up: glossary, API notes, sample links, competitors, course map. |
| [`research/`](research/) | Investigations and reviews that end in a finding, a decision or an open question: open questions, hosting, naming, risk review, design review. |
| [`solutions/`](solutions/) | How we handle one hard case: honest failure, URL cleaning, Slack pages, big PDFs, safe auto-filing. |
| [`design/`](design/) | Source files of the UI mockup ([V3](design/v3-mockup/README.md)). |

Where does a new doc go? A requirement goes in `feature-specs/`. A way to check it goes in `testing/`. A choice with reasons goes in `process/decision-log.md`. A fact you looked up goes in `reference/`. A question you answered by investigating goes in `research/`.

## IDs used in all docs

- **F-01 to F-20**: features. **NF-01 to NF-05**: non-functional rules. See the [PRD](product/mnemo-prd.md).
- **D-001 to D-020**: decisions. See the [decision log](process/decision-log.md).
- **Phases**: 0 to 10, then A, B, C. See the [phases overview](product/phases-overview.md).

## Rules for these docs

- Plain English. No calendar dates. Phases and sessions only.
- Anything not checked is marked **Unverified** or **Open question**. Do not treat it as fact.
- If a doc and the code disagree, fix the doc in the same session.

## Conflicts between docs

Building the visual pages found seven conflicts. Each was checked against the other doc, the decision log and the code, and is now settled:

| Conflict | Resolution |
| --- | --- |
| JSON output method (classification vs tech stack) | Already agreed: structured outputs with `messages.parse()` (D-025). |
| Render disk (storage vs tech stack) | The disk persists under its mount path, on a paid service, one instance (checked on the Render page). Price is still **Unverified**. |
| Two writers (storage vs D-022) | D-022 wins: the MCP server calls the HTTP API; the web server is the only writer (D-035 lock). |
| Empty `folder` (data model vs folders) | Already agreed and matches the code: `Unsorted` is stored as `null`; `prev_folder` holds the string `Unsorted`. |
| What is logged (data model vs folders) | The code writes only `open` and `folder_rejected`. Other events are marked "not written yet". Move and Undo are not logged (D-038). |
| Duplicate check in import (import vs phase 5) | D-037, accepted: exact repeats are skipped at import in phase 4; near-duplicates stay in phase 5. |
| Private mode details | Save behaviour is settled and matches the code. What is left is below. |

**Open question**, still for the owner:
- Are private bookmarks shown in the digest, the MCP server and search? A private bookmark is a link saved with `private <link>` in the chat: no page is fetched and no Claude call is made, so it has only the link, a title you give and your own note.
- The Anthropic data retention settings and the company AI policy result (owner will check later).
- The Render price (owner will check later).

## Known gaps

- You have not chosen your 5 or 6 starter folders yet.
- The design is chosen (V3, light and dark) but only as a mockup. It is not checked in a rendered page (see [design review](research/design-review-v1-v5.md) and [theming spec](feature-specs/theming-and-design-tokens.md)).
- Render price and storage rules are not checked (see [hosting check](research/hosting-check.md)).
- Claude API prices and PDF limits are not checked. The model name is checked (see [API notes](reference/api-notes.md)).

## Use with Claude Code

Put this `docs/` folder in the project root (`mnemo/docs/`). In `CLAUDE.md`, say: "Read `docs/README.md` first. Follow the spec for the feature you are building. Do not build anything that is not in a phase plan." See [working agreements](process/working-agreements.md).
