# Decision Log
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file records the big decisions for Mnemo in a short ADR style (ADR means architecture decision record). Each row has context, decision, status and consequences.

Status values: Accepted (agreed), Proposed (suggested, not yet built or agreed), Open (not decided).

| ID | Context | Decision | Status | Consequences |
| --- | --- | --- | --- | --- |
| D-001 | You chose to use only the Claude API. | Claude API only. | Accepted | Anthropic has no embedding API (lesson 34), so search uses no embeddings (D-006). Page text, URL and questions go to Anthropic. |
| D-002 | Anyone can read the code of a web page or an app (lessons 1 and 2). | The server holds the API key. Screens never hold it. | Accepted | One small Python server plus thin screens. See NF-01. |
| D-003 | The first idea was a command line. | Two screens: chat and bookmark page. | Accepted | Mock-ups in the plan use terminal text only to stay short. |
| D-004 | Claude could be wrong about whether text is a link or a question. | Plain code (a URL check) decides link versus question. | Accepted | This choice cannot be wrong in the way a model can. |
| D-005 | Auto-filing can hide a bookmark in the wrong folder. | Claude picks only from existing folders; Unsorted when unsure; code rejects unknown folder names; Move and Undo always visible; search ignores folders. | Accepted | Filing accuracy is measured on the Route set. See [safe auto-filing](../solutions/safe-auto-filing.md). |
| D-006 | Claude API only means no embeddings. | Chunk page text, rewrite the query, two BM25 indexes, merge with RRF, Claude picks the best 3. | Accepted | Search may be weaker for questions with very different words. The phase 5 eval shows how much. The query rewrite and pick step are the plan's own design, not in the course. See [embeddings alternatives](../research/embeddings-alternatives.md). |
| D-007 | Work is safest on your own computer first. | Local first, Render later. | Accepted | Render price and disk persistence are unverified. See [hosting check](../research/hosting-check.md). |
| D-008 | A native iPhone app needs Swift and, for a stable install, a paid Apple account. | iPhone Share Shortcut, not a native app. | Accepted | Whether the Shortcut works is unverified; test early. Fallback: paste in Safari. |
| D-009 | A browser tab does the same job as a window app. | The .deb app is phase C and is cut first. | Accepted | Low value; outside the course. |
| D-010 | A .dmg only works on a Mac and shows a warning when unsigned. | Mac .dmg is not planned. | Accepted | Add only if you ask. See [open questions](../research/open-questions.md). |
| D-011 | Your English is better for reading than writing. | English-only summaries in version 1. | Accepted | No language badge in version 1. The Vietnamese tutorial stays in the set as an extra case, not scored. `language` field is not in version 1. |
| D-012 | The host may not keep files between deploys. | All storage goes through `store.py`. | Accepted | If the host loses files, only the inside of `store.py` changes (to a database). See NF-03. |
| D-013 | Two sample links did not fit the seven types. | Add types `docs` and `other`. | Proposed | Not yet built. The eval will show if more types help. |
| D-014 | The project needed a name. | The name is Mnemo (was Bookmark Brain). | Accepted | Other software uses the name. Re-check before any public release. See [naming](../research/naming.md). |
| D-015 | People scan lists in different ways. | The bookmark page has a Grid, List and Compact switcher (F-05). | Accepted | Grid and List in phase 1; Compact in phase 3. The CSS `:has()` approach is unverified. |
| D-016 | Five mockups (V1 to V5) exist, and earlier ones felt like "AI slop". | Visual direction is not decided. | Open | Pick after phase 1 with real links. See [design review](../reviews/design-review-v1-v5.md). |
| D-017 | Page text goes to the API even for links you want to keep private. | Private mode (F-19): a link marked private is saved as link only and nothing is sent to the API. | Proposed | Ships in phase 3 if accepted. Adds a `private` field (proposed). |
| D-018 | Page text goes to the API. | Public links only while building. | Accepted | Check your company's AI policy before saving work links. |

## How to change a decision
1. Write the new row or change the status.
2. Say what changed in your [session note](session-log-template.md).
3. Update the specs that mention the decision.

## Open items
- D-016 is Open. Do not build final visual styling before it is decided.
- D-013 and D-017 are Proposed. Confirm or reject them before phase 3.

Related: [open questions](../research/open-questions.md), [risk review](../reviews/risk-review.md).
