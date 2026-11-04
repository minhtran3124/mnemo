# Mnemo Roadmap
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file puts the phases in order, in releases. It uses sessions (about 30 minutes each), not dates.

## Release order
| Release | Phases | What you get | Sessions |
| --- | --- | --- | --- |
| 1 (MVP) | 0, 1, 2, 3 | Save links, honest cards, eval score, filing with Move and Undo, private mode | about 10 |
| 2 | 4, then a 2-week test | Ask questions, import old pile, screenshots; real use test | 4, plus test |
| 3 | A, then B | Use from phone browser, then Share Shortcut | 4 + 1 |
| 4 | 5, 6, 7, 8, 9 | Better search and duplicates, PDFs and quotes, folder proposals, digest and roast, MCP server | 3 + 2 + 2 + 3 + 3 |
| Optional | 10, C | Dead-link doctor (or chart or replacement search); .deb window | 3 + 2 |

Suggested order from the plan: phases 0 to 4, the 2-week test, phase A, phase B, then phases 5 to 9. Phase B is tested early because it is unverified that the Shortcut works.

## Decision points
1. **After phase 3:** save only real links for one week. Check if you type the reason. If not, change the design before building more.
2. **After phase 4:** use the app 2 weeks and fill the success table in the [PRD](mnemo-prd.md). If results are weak, change the design before phase 5.

## What you can do after each phase
| Phase | Sessions | You can now |
| --- | --- | --- |
| 0 | 1 | Nothing visible. Project is safe and ready |
| 1 | 3 | Paste a link in chat, get a card, see a saved list |
| 2 | 3 | See if a change helps (three scores) |
| 3 | 3 | Trust cards and filing; Compact view; private mode |
| 4 | 4 | Ask, import, save screenshots |
| A | 4 | Use from phone browser |
| B | 1 | Share from iPhone |
| 5 | 3 | Find with other words; duplicate warning |
| 6 | 2 | Quotes and PDFs |
| 7 | 2 | Folder proposals |
| 8 | 3 | Digest and roast |
| 9 | 3 | Search from Claude Code |
| 10 | 3 | Optional dead-link fixes |
| C | 2 | Optional Ubuntu window |

## Totals
Phases 0 to 9: 27 sessions. A, B, C in the table: 7 sessions. Phase 10: 3 sessions. The plan also says A to C add "about 12" sessions, which does not match its own table (7). Open question: which number is right?

The plan's estimate is about 13 weeks at 3 sessions per week (a full 3 months). Real sessions per week is unknown, so treat 13 weeks as a guess. See [open questions](../research/open-questions.md).

## What to cut first
1. Phase 10 and phase C.
2. Phase 9 (MCP).
3. Caching and extended thinking in phase 8.
4. Router and parallel parts in phase 7.
5. Phase 6 (quotes and PDFs).
6. After the 2-week test: phase B and phase 5, only if the web page already solves the problem.

Never cut phases 0 to 4, phase A, or the eval in later phases. Cutting means you read the lessons but do not build.

Links: [phases overview](phases-overview.md), [risk review](../reviews/risk-review.md).
