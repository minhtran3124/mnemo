# Mnemo docs

Status: Draft v0.1 · Owner: KhoiTran · Phase: all

Mnemo is a personal AI bookmark app. You paste a link in a chat. The app reads the page, writes a short summary, picks a folder and saves it. You find things again by asking in your own words. It uses the Claude API only. These docs hold everything we decided before the first line of code.

The name was chosen by you. Other software already uses "mnemo" (see [naming](research/naming.md)). That is fine for a personal project. Check again before any public release.

## Start here

1. [Pre-start checklist](reviews/pre-start-checklist.md): what must be true before phase 0.
2. [PRD](product/mnemo-prd.md): what we build and why.
3. [Roadmap](product/roadmap.md) and [phases overview](product/phases-overview.md): in what order.
4. [Open questions](research/open-questions.md): what you still need to answer. None blocks phase 0.

## Visual pages

Four pages draw these docs as pictures. They are snapshots of `main` at commit `ce40e28`. They are private until you share them. The docs are the source of truth; if a page and a doc differ, fix the page.

| Page | Shows | Linked from |
| --- | --- | --- |
| [Roadmap](https://claude.ai/artifact/AJJLCpqJSUq927cvXRbBPx) | Phases, releases, sessions, decision points, what to cut | [roadmap](product/roadmap.md), [phases overview](product/phases-overview.md) |
| [User workflow](https://claude.ai/artifact/PH6PBSCNxy76aeVVijwsgQ) | How you save, find, file and ask; who decides each step | [PRD](product/mnemo-prd.md), [chat and intent](feature-specs/chat-and-intent.md) |
| [Architecture](https://claude.ai/artifact/HRJ54QxYXpooHoemp6uSgV) | Pages, server, `store.py`, Claude API, MCP; trust boundary; all decisions | [tech stack](product/tech-stack.md), [server API](feature-specs/server-api.md), [privacy](feature-specs/privacy-and-security.md) |
| [Data model](https://claude.ai/artifact/RjucLkUNCY5pWzD3RxJkpt) | Records, fields, files, bookmark lifecycle | [data model](feature-specs/data-model.md), [storage](feature-specs/storage.md) |

The design mockup (V3, light and dark) is linked from [frontend UI](feature-specs/frontend-ui.md).

Building these pages found conflicts between docs. They are not fixed yet: JSON output method (classification vs tech stack), Render disk (storage vs tech stack), two writers (storage vs D-022), empty `folder` (data model vs folders), what is logged (data model vs folders), duplicate check in import (import vs phase 5), private mode details. Open question: fix them in a separate PR.

## Folder map

| Folder | What is inside |
| --- | --- |
| [`product/`](product/) | PRD, roadmap, phases overview. [`product/plans/`](product/plans/) has one plan per phase (0 to 10, A, B, C). |
| [`feature-specs/`](feature-specs/) | One spec per feature area: data model, chat, page reading, filing, folders, views, search, import, API, privacy, storage. [`test-cases/`](feature-specs/test-cases/) has the golden sets and hard cases. |
| [`manual-testing/`](manual-testing/) | Test strategy, smoke checklist, the two-week user test, phone and Shortcut test. |
| [`process/`](process/) | How we work: agreements, definition of done, eval process, secrets, session log, decision log. |
| [`reference/`](reference/) | Glossary, course map, competitors, API notes to verify, sample links. |
| [`research/`](research/) | Open questions, local vs online, naming, hosting check, embeddings alternatives. |
| [`reviews/`](reviews/) | Risk review, design review of the five mockups, pre-start checklist. |
| [`solutions/`](solutions/) | Short notes on problems we already solved on paper: honest failure, URL cleaning, Slack pages, big PDFs, safe auto-filing. |

## IDs used in all docs

- **F-01 to F-20**: features. **NF-01 to NF-05**: non-functional rules. See the [PRD](product/mnemo-prd.md).
- **D-001 to D-020**: decisions. See the [decision log](process/decision-log.md).
- **Phases**: 0 to 10, then A, B, C. See the [phases overview](product/phases-overview.md).

## Rules for these docs

- Plain English. No calendar dates. Phases and sessions only.
- Anything not checked is marked **Unverified** or **Open question**. Do not treat it as fact.
- If a doc and the code disagree, fix the doc in the same session.

## Known gaps

- You have not chosen your 5 or 6 starter folders yet.
- The design is chosen (V3, light and dark) but only as a mockup. It is not checked in a rendered page (see [design review](reviews/design-review-v1-v5.md) and [theming spec](feature-specs/theming-and-design-tokens.md)).
- Render price and storage rules are not checked (see [hosting check](research/hosting-check.md)).
- Claude API prices and PDF limits are not checked. The model name is checked (see [API notes](reference/api-notes.md)).

## Use with Claude Code

Put this `docs/` folder in the project root (`mnemo/docs/`). In `CLAUDE.md`, say: "Read `docs/README.md` first. Follow the spec for the feature you are building. Do not build anything that is not in a phase plan." See [working agreements](process/working-agreements.md).
