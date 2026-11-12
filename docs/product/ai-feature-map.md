# AI feature map

Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file lists every feature of Mnemo, the personal hub. For each one it says whether the hub prototype has a screen, whether a spec exists, how the feature uses the Claude API, and what it may cost per month. It is the checklist to finish before any feature code: every row needs a screen and a spec first.

Hub prototype: [Mnemo personal hub](https://claude.ai/artifact/77KLF6DA2WFCMescbP92Vf) (private). Feature IDs (F-xx) come from [mnemo-prd.md](mnemo-prd.md).

## 1. Budget

- The owner has $100 a month of Claude API credit.
- Prices used below (per 1M tokens, input / output), from the Claude API price table as cached on 2026-11-03. **Unverified**: check the official pricing page before relying on them.
  - Haiku 5.5: $0.10 / $0.50 (prompts up to 100K tokens)
  - Sonnet 5.5: $2 / $10
  - Opus 5.5: $4 / $20
  - Batch API: 50% off. Cache reads: about 10% of the input price.
- Thinking tokens are billed as output. Real costs can be 2 to 5 times the numbers below. `mnemo/core/client.py` already logs token counts, so phase work must measure the real cost.
- Volumes per month are guesses for one person: 300 saves, 100 questions, 30 notes actions, 4 weekly digests, 30 daily digests.

**Estimate**: everything below on the suggested models costs about $15 to $25 a month. The budget is not the limit. The risk is a bug or a loop that spends the whole $100. That is why the spend guard (AI-01) comes first.

## 2. Feature map

Legend for "Screen": **Yes** = the hub prototype has it. **Part** = some states are missing. **No** = no screen.
Legend for "Spec": a file in `docs/feature-specs/`, or **None**.

### 2.1 Bookmarks (PRD F-01 to F-20)

| ID | Feature | Screen | Spec | Claude use | Model | Cost / month |
| --- | --- | --- | --- | --- | --- | --- |
| F-01, F-02 | Save with summary, honest failure | Yes | classification-and-filing.md, page-reading.md | One call per save. **Built.** | Haiku 5.5 (Sonnet if the eval wins) | $0.20 (Haiku), $4 (Sonnet) |
| F-03 | Auto-filing, Move, Undo | Yes | folders.md | Same call as save | Same | $0 extra |
| F-06 | Import the old pile | No | import.md | One save call per link, by Batch | Haiku 5.5, Batch | under $1 one time for 500 links |
| F-07, F-08 | Ask in plain words, with sources | Part: no "nothing found" state | ask-and-answers.md | Tool loop, about 3 turns | Sonnet 5.5, cached system prompt | about $3.50 |
| F-09 | "Do I have this?" | **Unverified** | duplicates.md | None for the same URL; one call for "similar" | Haiku 5.5 | under $0.50 |
| F-10 | PDFs and screenshots | Yes | pdf-and-screenshots.md | One call per file | Haiku 5.5 | about $0.50 |
| F-13 | Folder proposals | No | folders.md | One call over all titles | Sonnet 5.5 | under $1 |
| F-14 | Weekly digest | Part: no near-duplicates, no dead links | digest-and-roast.md | Claude writes only the "why now" lines | Sonnet 5.5, cache on the list | under $1 |
| F-15 | Roast | No | digest-and-roast.md | Claude writes words; code writes numbers | Sonnet 5.5 | under $0.50 |
| F-17 | Use from Claude Code (MCP) | No screen needed | mcp-server.md | None in Mnemo | None | $0 |
| F-18 | Dead-link doctor | Part: "Drop the old links?" only | None | Proposals only | Haiku 5.5 | under $0.50 |
| F-19 | Private mode | **Unverified** | privacy-and-security.md | None by design | None | $0 |

### 2.2 Hub features (in the prototype, not in the PRD)

These screens exist in the hub prototype, but no PRD row and no spec exist. They need both before code.

| ID (proposed) | Feature | Screen | Spec | Claude use | Model | Cost / month |
| --- | --- | --- | --- | --- | --- | --- |
| H-01 | Today page | Yes | None | Short "what to do today" text from code-picked items | Haiku 5.5 | under $0.50 |
| H-02 | Notes, with AI tidy and summary | Yes (no AI actions) | None | One call per action | Sonnet 5.5 | about $1 |
| H-03 | Ideas, draft an idea | Yes | None | One call per draft | Sonnet 5.5 | about $1 to $3 |
| H-04 | Calendar, proposed reading slots | Yes | None | None: code finds free slots | None | $0 |
| H-05 | Tasks | Yes | None | None at first | None | $0 |
| H-06 | Learning paths, learning log, review cards | Yes | None | One call to make a path; one per review card | Sonnet 5.5 for paths, Haiku for cards | about $1 to $2 |
| H-07 | Graph, "related in your graph" | Yes | None | Links by shared tags (code). No embeddings (D-001) | None, or Haiku to name clusters | $0 to $0.50 |
| H-08 | Daily digest and "Today's listen" | Yes | None (the spec is weekly) | Short text per item | Haiku 5.5 | about $1 |
| H-09 | Capture by email forward and Telegram bot | Yes | None | Same save call as F-01 | Haiku 5.5 | inside F-01 |
| H-10 | Scheduled jobs, "What the jobs checked" | Yes | None | Runs digest, dead links and review cards on a timer | Batch where it can wait | inside the rows above |
| H-11 | Goal mode | Yes | None | **Open question**: what it does | **Open question** | **Open question** |

### 2.3 New AI rows (from this plan)

| ID (proposed) | Feature | Screen | Spec | Claude use | Model | Cost / month |
| --- | --- | --- | --- | --- | --- | --- |
| AI-01 | Spend guard and AI usage page | No | None | None. Code adds up tokens from each response, warns at $60, stops new AI calls at $80, saves links only | None | $0 |
| AI-02 | Model and effort per feature, in Settings | No | None | Picks the model per row above, from `mnemo/core/config.py` | None | $0 |

## 3. What the prototype still needs

Screens to add to the hub prototype before code:

1. **AI usage page** (AI-01): this month's spend against $100, cost per feature, the warn and stop lines, and the "AI paused, links saved only" banner.
2. **Settings › AI models** (AI-02): model and effort per feature, with the cost estimate beside each.
3. **Import** (F-06): pick a file, see the count and cost estimate, confirm, progress in batches of about 20.
4. **Ask, "nothing found"** (F-07): the honest empty answer.
5. **Weekly digest, full** (F-14, F-15): near-duplicates, dead links and the roast, each number from code.
6. **Folder proposals** (F-13): accept or reject each proposed folder.
7. **Notes AI actions** (H-02): Tidy, Summarize, Turn into idea, each with a preview before it changes the note.

## 4. Open questions

- **Open question**: Calendar and email need private data. D-018 says public links only while building. Keep H-04 and H-09 as prototype only until D-018 changes?
- **Open question**: "Today's listen" needs text to speech. The Claude API has no voice output, so this needs another service and another cost. Keep it, or drop it?
- **Open question**: The prototype has a daily digest; the spec has a weekly one. Which one, or both?
- **Open question**: What is Goal mode (H-11)?
- **Open question**: Should H-01 to H-11 get F numbers in the PRD, or stay a separate hub list?
