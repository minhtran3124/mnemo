# Risk Review
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file expands the plan's risk table. Likelihood and impact are my judgement (Low, Medium, High), not measured. The biggest risk is that you stop using the app, not that the code fails.

| # | Risk | Likelihood | Impact | Owner action | Early signal |
| --- | --- | --- | --- | --- | --- |
| R-01 | You stop using it | Medium | High | Keep saving to one box. Run the [two-week test](../testing/two-week-user-test.md). Change the design if it fails. | Fewer than 10 saves in 2 weeks; you use browser bookmarks instead |
| R-02 | One wrong summary breaks trust | Medium | High | Show page status on every card. Keep the honest-failure and faithful-summary checks. | You find an invented fact in a card |
| R-03 | The reason field stays empty | Medium | Medium | Test in phase 3. If you do not type it, change the design. | Most saves have `reason_source` = guess |
| R-04 | Many pages cannot be read | High | Medium | Count unreadable pages among real links. Keep the Paste text path. | Many "Page not read" cards (the X post and Slack link already failed) |
| R-05 | Privacy: page text goes to the API | High | Medium | Public links only (D-018). Check company AI policy. Private mode F-19 is accepted (D-017): a private link is saved link only. | You want to save a private or work link |
| R-06 | Site rules | Low | Unknown | Keep saved text on your disk; do not share it. Not legal advice. | Plan to share or publish saved text |
| R-07 | Project too big | Medium | High | Finish phases 0 to 4, use it for 2 weeks, then continue. See [roadmap](../product/roadmap.md). | A phase takes far more sessions than planned |
| R-08 | The eval is subjective | Medium | Medium | Held-out set. Read 3 results every run. Fix the grader first. | You disagree with the grader often |
| R-09 | Structured output ends in a refusal or a `max_tokens` cut, or breaks the schema | Unknown | Low | Phase 1 treats both stop reasons as invalid, retries once, then saves link only. Code checks tag count and summary length. | JSON errors in phase 1 |
| R-10 | Caching does not help | Medium | Low | Read the two cache fields in `usage`. Keep caching only if numbers show gain. | Cache read tokens stay at zero |
| R-11 | An agent changes your data | Low | High | Agents and folder tools only propose. You approve. | Any change made without a click |
| R-12 | Cost grows | Medium | Medium | `max_tokens`, maximum page length, smaller model while building, spending cap. | Weekly spend above your limit |
| R-13 | A public server spends your money | Medium (if online) | High | Login, `max_tokens`, page length limit, spending cap (phase A). | Unknown requests in the log |
| R-14 | Shortcut and .deb are outside the course | Medium | Low | Treat time estimates as guesses. Test early. Cut phase C first. | Phase B takes more than one session |
| R-15 | Auto-filing hides a bookmark | Medium | Medium | Unsorted when unsure, Move and Undo visible, search ignores folders (D-005). | Bookmarks you cannot find in expected folders |
| R-16 | Search is weaker without embeddings | Medium | Medium | Phase 5 eval shows the gap. See [embeddings alternatives](../research/embeddings-alternatives.md). | Find rate below target |

## Privacy and local-first risks
| # | Risk | Likelihood | Impact | Owner action | Early signal |
| --- | --- | --- | --- | --- | --- |
| P-01 | Server bound to `0.0.0.0` exposes your bookmarks | Low | High | Bind to `127.0.0.1`. Check in the [smoke checklist](../testing/smoke-checklist.md). | The page opens from another device |
| P-02 | `.env` committed to git | Low | High | `.gitignore` first. See [git and secrets](../process/git-and-secrets.md). | `.env` in `git status` |
| P-03 | Key appears in page source or logs | Low | High | Search page source for the key. Never print the key. | Key found in any output |
| P-04 | Page text includes private data from a page behind a login | Medium | Medium | Do not save logged-in pages. Use private mode if accepted. | A card shows content from a members-only page |
| P-05 | Host loses files after deploy | Unknown | High | Verify before phase A. See [hosting check](../research/hosting-check.md). Back up before deploy. | Empty bookmark list after a deploy |
| P-06 | Unverified API data retention | Unknown | Medium | Read the policy. Record the answer in [API notes](../reference/api-notes.md). | Policy conflicts with what you save |
| P-07 | Local data has no backup | Medium | High | Plain files you can copy. Add a simple backup habit. Open question: how often. | Disk problem or deleted folder |

Related: [decision log](../process/decision-log.md), [local vs online](../research/local-vs-online.md).
