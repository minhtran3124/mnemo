# Test Strategy
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

This file explains the three levels of checking in Mnemo and what a person tests by hand on each screen.

## Three levels

| Level | Who runs it | What it finds | When |
| --- | --- | --- | --- |
| Code checks | The computer | Wrong format, wrong folder name, missing fields, tracking parts left in a link | Every change |
| Eval | The computer plus a model grader | Whether tags, summaries and answers got better or worse | Every prompt change (from phase 2) |
| Manual test | You | Things only a person sees: confusing text, a card that looks wrong, a phone layout that breaks | After every phase |

Code checks are fast and exact. The eval is a measure, not a proof (see [eval process](../process/eval-process.md)). Manual testing is the only level that finds "this feels wrong". Use all three. Do not skip manual testing because the score is high.

## What to test by hand on each screen

### Screen 1: Chat
| Check | Expected |
| --- | --- |
| Paste a readable public link | A card with title, type, 3 tags, summary, "Filed in", Move, Undo |
| Paste an unreadable link (for example a Slack link) | A "Page not read" card, no summary, a Paste text field |
| Paste a link with `fbclid` or `utm_*` | The saved link has no tracking part |
| Type a question | Up to 3 bookmarks, each with a reason, or "nothing found" |
| Type a question that has no answer in your list | "Nothing found" and no invented bookmark |
| Click Undo | The folder change is reversed and the card says so |
| Mark a guess | A guessed reason is labelled "guess" |

### Screen 2: Bookmark page
| Check | Expected |
| --- | --- |
| Folder list | Each folder shows a count that matches the rows |
| Filters and search | Type, tag and search change the list; search ignores folders |
| Row content | Title, reason or "guess", date, "page not read" badge when needed |
| Open, Move, Delete | Each works; Delete asks before it acts |
| View switcher (F-05) | Grid and List in phase 1, Compact from phase 3 |

Test cases for each feature are in [test-cases](../feature-specs/test-cases/README.md). Sample links are in [sample links](../reference/sample-links.md). Hard cases are in [hard cases](../feature-specs/test-cases/hard-cases.md).

## Entry and exit per phase

| Phase | Entry (start when) | Exit (stop when) |
| --- | --- | --- |
| 0 | Python and Claude Code installed, key in `.env` | A script gets an answer; a second call shows memory; `.env` not in git |
| 1 | Phase 0 exit passed | 5 public links give readable cards; an unreadable page is saved as link only; no invented fact |
| 2 | Phase 1 exit passed | One command scores 20 pages and prints three numbers; baseline run twice |
| 3 | Phase 2 exit passed | 3 or more prompt versions compared; Route set scored; Move and Undo work; 10 real saves tried |
| 4 | Phase 3 exit passed | Questions and trick questions run; import works in small batches; screenshots save |
| 5 | Phase 4 exit and the two-week test | Retrieval eval compares three methods; 5 planted duplicates caught |
| 6 | Phase 5 exit passed | A PDF saves; an answer shows a quote that exists in the page text |
| 7 to 10 | Previous phase exit passed | See each phase plan in [phases overview](../product/phases-overview.md) |
| A | Phases 0 to 4 done | Server online with login and spending cap; chat works on a phone browser |
| B | Phase A done | Share to the server from the iPhone works, or the fallback is documented |
| C | Phase A done | A `.deb` file installs and opens the chat page |

Run the [smoke checklist](smoke-checklist.md) at every exit. Phone checks are in [phone and shortcut test](phone-and-shortcut-test.md).

## Open questions
- Open question: Which phone and browser versions you will use for testing. Record them in your session note.
