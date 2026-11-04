# Chat and intent (Screen 1)

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1

This file describes the chat screen and how plain code decides if a message is a link or a question.

## Purpose

The chat is the main way to save and to ask. It supports F-01, F-02, F-03 and F-04, and decision D-003 (chat plus bookmark page, not a command line) and D-004.

## Scope

In: Screen 1 layout, intent rule, card, messages, Move, Undo, paste-text path.
Out: how Claude classifies (see [classification-and-filing.md](classification-and-filing.md)); the second screen (see [bookmark-page-and-views.md](bookmark-page-and-views.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| CI-01 | Plain code decides if a message is a link or a question. Claude does not decide (D-004). |
| CI-02 | The rule uses a URL regex (a pattern that finds web addresses). A message with a web address is a save. Otherwise it is a question. |
| CI-03 | A saved link shows a card: title, type, 3 tags, summary, "Filed in", and the buttons Move and Undo. |
| CI-04 | An unreadable page shows a "Page not read" card with a Paste text field (F-02). |
| CI-05 | The reason is optional and one line. If skipped, the app guesses and marks it "guess". |
| CI-06 | A question returns up to 3 bookmarks (see [ask-and-answers.md](ask-and-answers.md)). |

## Behavior and rules

- Saving needs no choices. You paste a link and get a card.
- You can write the link and a reason in the same message, for example a link followed by "for login test cases". The reason is the text that is not the link.
- Move and Undo stay visible on every card (D-005). See [folders.md](folders.md).
- The paste-text path: when a page cannot be read, you paste the page text. The app then runs the normal save on that text. It is the same path used for Slack messages: you paste the message text and the app finds the links in it (see [import.md](import.md)).
- The app never writes a summary of text it did not see (NF-04).

### Messages (exact wording to start with)

| Case | Text |
| --- | --- |
| Page not read | "I could not read this page. Saved the link only." |
| Slack link | "I cannot open Slack links. Paste the message text." |
| Nothing found | "nothing found" |
| Exact duplicate | "You saved this already" |
| Near-duplicate | "You saved something similar" |

Final wording: Open question.

## Edge cases

| Input | Result |
| --- | --- |
| Two links in one message | Save both, one card each. Do not ask (decided). The text that is not a link is the reason for each link. |
| A link inside a question | Treated as a link (regex wins). |
| Text with no link that is meant as a note | Treated as a question until a note path exists. A note path is wanted (decided); how the user marks a note is an open question. |
| Empty message | Ignored. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | A message with a URL never goes to the question path, and the reverse. Tested with code, no API call. |
| 2 | A readable page gives a card with all CI-03 parts. |
| 3 | An unreadable page gives the "Page not read" card and a null summary. |
| 4 | Undo returns the bookmark to its earlier folder. |

## Tests

[route-set.md](test-cases/route-set.md), [hard-cases.md](test-cases/hard-cases.md).

## Open questions

- How the user marks a plain note, since CI-02 sends text without a link to the question path.
- How long Undo stays available (skipped for now; no time limit is set).
- Final message wording.

Decided: several links in one message are all saved, with no question asked.
