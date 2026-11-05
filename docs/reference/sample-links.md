# Sample links

Status: Draft v0.1 · Owner: KhoiTran · Phase: 2 (golden sets), used from phase 1

This file lists the real links you sent while we made the plan, what a fetch tool did with each one, and what each link tests. It is the input for the [save golden set](../feature-specs/test-cases/save-golden-set.md), the [route set](../feature-specs/test-cases/route-set.md) and the [hard cases](../feature-specs/test-cases/hard-cases.md).

**Read this first.**
- "Result" is what the planning tool saw when it read the page. Your own fetcher may behave differently.
- "Type (proposed)" is a guess for the test set. It is not verified. Fix it when you write your expected answers.
- Where the full address was not kept, the link is shortened with "…". Copy the full address from your own list before you save the page text to `evals/golden/`.
- The plan says "20 different links". Counting the rows below gives 21. Decide which 20 go into the Save set. Keep 5 as the held-out set (see [eval process](../process/eval-process.md)).

## Links

| # | Link | Result | Type (proposed) | What it tests |
| --- | --- | --- | --- | --- |
| 1 | `https://x.com/addyosmani/article/2117512471930167377` (an X post; link given by the owner on 2026-11-05) | The planning tool could not read X posts. Unverified: whether Mnemo's own fetcher can. | link only | Honest failure. Summary is null. Paste-text path. |
| 2 | `dev.to/fisher_shenfisher_1c32/pocket-alternative-2026-the-complete-guide-after-pockets-shutdown-4mpe` | Readable. Article about Pocket alternatives. Promotional. | article | Normal path. Check that the summary has only facts from the page. |
| 3 | `airtable.com` (home page) | Readable, mostly marketing text. | tool | Weak page. Summary must stay general. |
| 4 | `huggingface.co/blog/sionic-ai/claude-code-skills-training` | Readable. | article | Normal article. |
| 5 | `thehackernews.com/…/brotli-decoder-flaw-behind-nodejs-rce` | Readable. The tool wrongly named the site "Hacker News". | article | Faithful summary. Near-duplicate of #6. |
| 6 | `bleepingcomputer.com/…/critical-http2shell-brotli…` | Fetch error. | link only | Honest failure. Retry once. Near-duplicate of #5. |
| 7 | `github.com/subframe7536/maple-font` | Readable. | github_repo | Tags must not be forced into AI topics. |
| 8 | `github.com/gyoridavid/ai_agents_az` | Readable. | github_repo | Normal repo. |
| 8b | Same as #8 with a long `fbclid` tracking part | Not fetched separately. | (same as #8) | Exact duplicate after URL cleaning. Do not count as a separate link. |
| 9 | `april-zhu.com/colorfigures` | Readable. | tool | Tool landing page. |
| 10 | `youtube.com/watch?v=lDrAZ1wAyVs` | Only the description is readable. | video_page | Card must say "from the description only". |
| 11 | `sites.slopengineer.dev/s/428d78199c11ceead8338938e2fe0844/` | Readable. Written in Vietnamese. | article | Language rule. English summary only in version 1. Extra case, not scored. |
| 12 | `claude.dev/…/building-effective-agent-automations` | Readable. | article | Normal article. |
| 13 | `claude.dev/…/solving-code-review-at-anthropic` | Readable. | article | Normal article. |
| 14 | `wearedevelopers.com/videos` | Readable. A list of many videos. | other | Index page. Needs the `other` type (D-013). |
| 15 | `langchain.com/…/revamping-skills-in-deep-agents` | Readable. | article | Normal article. |
| 16 | `airtable.com/developers/web/api/introduction` | Readable. API reference. | docs | Needs the `docs` type (D-013). |
| 17 | `github.com/Donchitos/Claude-Code-Game-Studios` | Readable. | github_repo | Normal repo. |
| 18 | `langchain.com/…/jev-is-now-available-in-langsmith-evals` | Readable. Product announcement. | article | Close to your interest: agent evaluation. |
| 19 | `arxiv.org/html/2606.09498v1` | Readable. Math appears as raw markup. | article + tag `paper` | Summary must not copy raw math. |
| 20 | `uber.com/us/en/blog/ai-code-cleanup/` | Readable. Code is in images. | article | Summary may miss facts that are only in images. |
| 21 | `contextfirst.blog/superlite-hand-an-agent-a-spec/` | Readable. Long first-person article. | article | Normal long article. |

## Phase 1 test set

The 5 links for the [phase 1 plan](../product/plans/phase-1-chat-and-bookmark-pages.md). All have a full address and fit the existing types (no `docs` or `other` needed). Row 1 is a public login page, because the X post (#1 above) turned out to be readable by Mnemo's own fetcher.

| # | Link row | Why it is in the set |
| --- | --- | --- |
| 1 | `https://www.instagram.com/accounts/login/` (not one of the 21 rows) | The unreadable case: link only, null summary, paste text works. Checked on 2026-11-05: Mnemo's own fetcher saves it as `unreadable` with a null summary. |
| 2 | #2, dev.to Pocket guide | A promotional article: the summary must hold only facts from the page. |
| 3 | #4, Hugging Face blog | A normal article. |
| 4 | #7, `subframe7536/maple-font` | A GitHub repo through the GitHub API; tags must not be forced into AI topics. |
| 5 | #8, `gyoridavid/ai_agents_az` | A GitHub repo. Then paste it again with `?fbclid=abc` added: it must be recognized as the same `url_clean`. |

Informational, not part of the 5: the X post (#1 in the table above) is readable by Mnemo's own fetcher (`page_status` ok, summary written from the page text on the 2026-11-05 run). It no longer tests the unreadable path. **Unverified:** whether it stays readable on later runs. `https://www.linkedin.com/login` also saved as link only. `https://www.facebook.com/login/` was read (`page_status` ok), so it does not test the unreadable path.

## Hard cases that are not in the 20

| Sample | Result | Where it is tested |
| --- | --- | --- |
| PDF book "AI-Ready PostgreSQL 18" (580 pages, 14.6 MB) | Pages 1 to 3 are a print cover, a title page and a copyright page. | [Hard cases](../feature-specs/test-cases/hard-cases.md), [big PDFs](../solutions/big-pdfs.md) |
| A Slack message link (`secretboth.slack.com/archives/…`) | Cannot be opened. It needs a sign-in. | [Slack and login pages](../solutions/slack-and-login-pages.md) |
| Screenshot of an X post by @0xShoopy about a "10-page PDF" | The image does not support the claim in the post. Text is cut ("Show more"). No URL. | [PDF and screenshots](../feature-specs/pdf-and-screenshots.md) |
| `about:blank#blocked` | Not a link. A browser placeholder. | Not a test. Send the real link if you still have it. |

## Still missing

- A page in another language besides Vietnamese. Postponed because summaries are English-only in version 1.
- Links from your Slack, phone notes and messages. Add them in phase 4 (import).
