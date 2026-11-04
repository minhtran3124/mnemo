# Mnemo Product Requirements (PRD)
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file says what Mnemo must do, for whom, and how we will know it works. Mnemo was called "Bookmark Brain" before. The name is used by other software, so check it again before any public release (see [naming](../research/naming.md)).

## 1. Problem and promise
**Problem.** You save links in three places: browser bookmarks, a notes app and messages to yourself. You cannot find a link you saved. Links go in and never come out. Unverified guess: you also forget why you saved a link, and you stop opening the pile.

**Promise.** Saving takes seconds and needs no decisions. You ask in your own words and get the link back, with the reason you saved it. Once a week the app tells you what is worth your time.

## 2. Target user and jobs
The user is one person: the owner. Public links only while building (D-018).

| # | When I... | I want to... | So that... |
| --- | --- | --- | --- |
| 1 | see a useful repo or article | save it in seconds, with no choices | I do not lose it or lose my focus |
| 2 | remember "something about caching" | ask in my own words | I get the link and why I saved it, not 200 links |
| 3 | start a task, such as test cases for a login page | ask "what do I already have about this?" | I reuse what I found |
| 4 | find a link I might have saved before | paste it and ask "do I have this?" | I do not collect duplicates |
| 5 | have 20 free minutes | get three things to read | the pile gets smaller |
| 6 | feel the list is messy | see a proposed folder structure | I decide what changes |
| 7 | open an old link that is dead | see all dead links in one list | I remove or replace them |
| 8 | start a Monday | read a short, funny comment about my habits | I feel like acting on the pile |
| 9 | have links in browser bookmarks, a notes app and messages | bring them all into one place | I stop searching three places |

These jobs are guesses. Edit them if they are wrong.

## 3. Four product rules
1. Saving must cost almost nothing.
2. Be right, or say you are not sure. Never write a summary of text the app did not see.
3. You stay in control. The app proposes; it never moves or deletes alone.
4. Give something back every week.

## 4. Goals and non-goals
**Goals:** get links back (not only store them); keep data in plain files you own; measure quality; work on laptop, then phone.

**Not served on purpose:** sharing with a team, reading pages inside the app, a browser extension. **Not planned:** Mac .dmg app (D-010), native iPhone app (D-008).

**Local-first and privacy.** The server runs on your own computer first (D-007) and binds to `127.0.0.1`, never `0.0.0.0`. With the Claude API only, page text, URL and questions go to Anthropic. Check your company AI policy before saving work links. See [privacy and security](../feature-specs/privacy-and-security.md).

## 5. Features
| ID | Feature | Priority | Phase | Acceptance (one line) |
| --- | --- | --- | --- | --- |
| F-01 | Quick save with a reason | Must | 1, 3 | A link alone gives a card; reason is optional and marked "guess" if the app wrote it |
| F-02 | Honest failure | Must | 1 | Unreadable page: link-only record, null summary, Paste text option |
| F-03 | Auto-filing (Move, Undo) | Must | 3 | Folder is an existing one or Unsorted; unknown folder rejected; Move and Undo visible |
| F-04 | Two screens: chat and bookmark page | Must | 1 | Both pages run on your computer |
| F-05 | Views: Grid, List, Compact | Should | 1 (Grid, List), 3 (Compact) | Switcher changes the view without reload loss of filters |
| F-06 | Import the old pile | Must | 4 | Browser file or pasted text; count and cost estimate first; batches of about 20 |
| F-07 | Ask in plain words | Must | 4, 5 | Up to 3 links with reasons; trick questions give "nothing found" |
| F-08 | Answers show sources | Should | 4, 6 | Each answer names its bookmarks; quotes exist in page text |
| F-09 | "Do I have this?" warning | Should | 5 | Same URL: "saved already"; similar: "saved something similar" |
| F-10 | PDFs and screenshots | Should | 4 (screenshots), 6 (PDF) | Both work like a link; size check before the API call |
| F-11 | Use from anywhere | Should | A | Online, login, spending cap, works on iPhone browser |
| F-12 | iPhone Share Shortcut | Should | B | Share menu sends the link; card appears in chat |
| F-13 | Folder proposals | Should | 7 | Accept or reject each folder; every bookmark has one folder |
| F-14 | Weekly digest | Should | 8 | Three reads, near-duplicates, dead links |
| F-15 | Roast | Could | 8 | Every number equals the code's count |
| F-16 | Ubuntu .deb window | Could | C | .deb installs and opens the chat page |
| F-17 | Use from Claude Code (MCP) | Could | 9 | Inspector tests pass; Claude Code finds a bookmark |
| F-18 | Dead-link doctor | Could | 10 | Proposals only; you approve |
| F-19 | Private mode (proposed) | Should | 3 | A private link is saved as link only; nothing goes to the API |
| F-20 | Quality eval harness | Must | 2 | One command prints three scores |

## 6. Non-functional requirements
| ID | Requirement |
| --- | --- |
| NF-01 | API key only on the server |
| NF-02 | Cost limits: max_tokens, max page length, spending cap |
| NF-03 | Bookmarks in plain files; all access through `store.py` ([storage](../feature-specs/storage.md)) |
| NF-04 | Honesty: no summary of unseen text; guesses marked |
| NF-05 | UI: touch targets at least 44px, contrast at least 4.5:1, visible focus, works at 390px width |

## 7. Success measures (all are proposals; set them before you start, do not change after seeing results)
| Question | Measure | Proposed rule |
| --- | --- | --- |
| Do I use it? | Saves in first 2 weeks | At least 10 |
| Is saving easy? | Saves where you typed only the link | Most saves |
| Do I trust it? | Of last 20 saves, tags kept | At least 15 of 20 |
| Is it honest? | Summaries with a fact not on the page (10 checked by hand) | None |
| Can I find things? | Right bookmark in top 3 for 15 questions | Set after first baseline |
| Faster than my browser? | 5 real needs, timed | Faster in at least 3 of 5 |
| Do I come back? | "Read next" items opened | Set after first digest |
| Worth the cost? | API spend per week | Under a limit you set |

See [two-week user test](../manual-testing/two-week-user-test.md).

## 8. Assumptions
Python; Claude Code writes most code; 30-minute sessions, about 3 per week (real number unknown); public links only; page fetcher written with Claude Code (GitHub repos via the official GitHub API); models set in one config file; search with Claude API only (no embeddings, D-006); storage in JSON and text files.

## 9. Constraints
Budget about $10 per month for hosting and API together (Unverified). 30-minute sessions. Python. Claude API only (D-001). Public links only while building (D-018).

## 10. Top 5 risks
1. You stop using the app. 2. One wrong summary breaks trust. 3. The reason field stays empty. 4. Many pages cannot be read. 5. An online server spends your money. Details: [risk review](../reviews/risk-review.md).

## 11. Open questions
See [open questions](../research/open-questions.md). Examples: starter folders, real sessions per week, visual direction (D-016).
