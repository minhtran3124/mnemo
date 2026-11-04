# Two-Week User Test
Status: Draft v0.1 · Owner: KhoiTran · Phase: 4

This file is a daily log and a decision rule for the two weeks of real use. It tells you whether Mnemo is useful. The code can pass every check and still be a product you do not use.

All targets below are proposed. Change them before you start. Do not change them after you see the results.

## When to run it
Use phases 0 to 4 for two weeks with real, public links. Public links only (decision D-018). Then stop and read the table.

## Measures

| Question | Measure | How you get it | Proposed target |
| --- | --- | --- | --- |
| Do I use it? | Links saved with the app in 2 weeks | The app counts saves | At least 10 |
| Is saving easy? | Share of saves where you typed only the link | The app logs it | Most saves need no extra typing |
| Do I trust it? | Of your last 20 saves, tags kept unchanged | You count | At least 15 of 20 |
| Is it honest? | Summaries with a fact not on the page | You check 10 summaries by hand | None |
| Can I find things? | For 15 questions you wrote, right bookmark in top 3 | The retrieval eval | Set after the first baseline |
| Is it faster than my browser? | For 5 real needs, did `ask` find the link faster | You time it | Faster in at least 3 of 5 |
| Do I come back? | Share of "read next" items you opened | The `open <id>` log | Set after the first digest |
| Is it worth the cost? | API spend per week | The app logs tokens | Under a limit you set |

Open question: the limit for weekly API spend. Set it before day 1.

## Daily log template
Copy one row per day.

| Day | Links saved | Typed only the link (count) | Reason typed (count) | Tags changed (count) | Questions asked | Found it? (yes / no) | Trouble or surprise |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |
| 9 | | | | | | | |
| 10 | | | | | | | |
| 11 | | | | | | | |
| 12 | | | | | | | |
| 13 | | | | | | | |
| 14 | | | | | | | |

## Final summary
| Measure | Result | Target met? |
| --- | --- | --- |
| Links saved | | |
| Saves with only the link | | |
| Tags kept (of last 20) | | |
| Invented facts (of 10 checked) | | |
| Faster than browser (of 5) | | |
| Weekly API spend | | |

## Decision rule
- If most targets are met, continue with phase A, then the Shortcut (phase B), then phases 5 to 9.
- If "Do I use it?" fails, the problem is the product, not the code. Change the design before you build phase 5. Write down why.
- If "Is it honest?" fails, stop. Fix honesty first (see [honest failure](../solutions/honest-failure.md)).
- If you do not type the reason, change the reason design (decision point after phase 3).
- Phase B and phase 5 can be cut if the web page alone already solves your problem.

Related: [risk review](../reviews/risk-review.md), [smoke checklist](smoke-checklist.md).
