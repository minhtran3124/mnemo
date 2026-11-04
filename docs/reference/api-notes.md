# API Notes
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file lists things to check in the official Claude documents before you build. Nothing here is a verified fact. Each item is Unverified until you fill in the answer and the date you checked.

Use only the official documents (the Claude API docs, the Console, and the course lessons). Do not copy numbers from blogs.

| # | Item | Why it matters | Lesson | Phase where it matters | Status | Answer | Date checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Current model names | `config.py` sets models in one place; you need the real names | Plan assumption 6 | 0 | Unverified | | |
| 2 | Model prices (input and output tokens) | The budget is about $10 per month for hosting and API together | Not in the plan | 0, 2, A | Unverified | | |
| 3 | PDF page limit and file size limit | The sample PDF has 580 pages and 14.6 MB; code checks size before the call | 41 | 6 | Unverified | | |
| 4 | Prefill support by model | Phase 1 uses prefill plus stop sequence for JSON; the lesson does not say which models accept it | 8 | 1 | Unverified | | |
| 5 | Minimum length for prompt caching | Below the minimum, caching is skipped with no error | 44 | 8 | Unverified | | |
| 6 | Citations: how they work with PDFs and text | Needed for quotes that exist in the page text | 42 | 6 | Unverified | | |
| 7 | Rate limits for your account | Import runs in batches of about 20 | Not in the plan | 4 | Unverified | | |
| 8 | Data retention policy for the API | Page text, URL and questions go to Anthropic | Not in the plan | 0, 3 (F-19) | Unverified | | |
| 9 | Image input limits for screenshots | Screenshots are sent as image blocks | 40 | 4 | Unverified | | |
| 10 | Spending limit in the Console: how to set it and what it does | NF-02 needs a spending cap | Not in the plan | 0, A | Unverified | | |
| 11 | Web search tool options (`max_uses`, `allowed_domains`) | Only if you build the optional replacement search | 31 | 10 | Unverified | | |
| 12 | Extended thinking: which models and cost | Tried on `folders` only | 45 | 8 | Unverified | | |

## How to fill this table
1. Open the official page.
2. Write the answer in your own words, short.
3. Write the session number when you checked it (not a calendar date).
4. Change Status to Checked.
5. Update the spec that depends on it.

## Rules
- Do not state an Unverified item as fact in any other doc.
- If the official page and the course lesson differ, trust the official page and write the difference here.
- Prices and limits change. Check again before phase A.

Related: [hosting check](../research/hosting-check.md), [open questions](../research/open-questions.md), [git and secrets](../process/git-and-secrets.md).
