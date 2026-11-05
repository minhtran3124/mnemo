# Chat and intent (Screen 1)

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1

This file describes the chat screen and how plain code decides if a message is a link or a question.

Visual page: [User workflow](https://claude.ai/artifact/PH6PBSCNxy76aeVVijwsgQ). It is a snapshot of `main` at commit `ce40e28` and is private until you share it. This file is the source of truth; if they differ, fix the page.

## Purpose

The chat is the main way to save and to ask. It supports F-01, F-02, F-03 and F-04, and decision D-003 (chat plus bookmark page, not a command line) and D-004.

## Scope

In: Screen 1 layout, intent rule, card, messages, Move, Undo, paste-text path.
Out: how Claude classifies (see [classification-and-filing.md](classification-and-filing.md)); the second screen (see [bookmark-page-and-views.md](bookmark-page-and-views.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| CI-01 | Plain code decides if a message is a link or a question. Claude does not decide (D-004). |
| CI-02 | The rule uses a URL regex (a pattern that finds web addresses). A message with a web address is a save. Otherwise, a message that matches `note <id> <text>` edits the reason of that bookmark. Anything else is a question. |
| CI-03 | A saved link shows a card: title, type, 3 tags, summary, "Filed in". From phase 3 the card also has the buttons Move and Undo. Phase 1 has no folders, so "Filed in" is always Unsorted and there are no buttons. |
| CI-04 | An unreadable page shows a "Page not read" card with a Paste text field (F-02). |
| CI-05 | The reason is optional and one line. If skipped, the app guesses and marks it "guess". |
| CI-06 | A question returns up to 3 bookmarks (see [ask-and-answers.md](ask-and-answers.md)). |
| CI-07 | The chat is saved. After a reload the page shows the earlier messages and cards again, from `data/chat.jsonl` and the bookmark records (DM-06). |
| CI-08 | Every card shows the bookmark number, so the user can write `note <id> <text>`. |

## Behavior and rules

- Saving needs no choices. You paste a link and get a card.
- You can write the link and a reason in the same message, for example a link followed by "for login test cases". The reason is the text that is not the link. Not built yet: in phase 1 the text around a link is ignored and Claude's guess is kept. Use `note <id> <text>` (own ticket) to set a reason.
- From phase 3, Move and Undo stay visible on every card (D-005). See [folders.md](folders.md).
- The paste-text path: when a page cannot be read, you paste the page text. The app then runs the normal save on that text. Pasted text under 40 characters is saved as link only with no summary. It is the same path used for Slack messages: you paste the message text and the app finds the links in it (see [import.md](import.md)).
- The app never writes a summary of text it did not see (NF-04).

### Messages (the wording of the V3 mockup; see [ui-reference.md](ui-reference.md))

| Case | Text |
| --- | --- |
| Page not read | "I could not read this page. I saved the link only." |
| Slack link | "I cannot open Slack links. I saved the link only." Then: "Copy the message in Slack and paste it here. I will find the links in it." |
| Nothing found | "nothing found" |
| A question in phase 1 (asking is not built yet) | "I can only save links for now. Asking comes later." |
| Exact duplicate | "You saved this already" |
| Near-duplicate | "You saved something similar" |

Final wording: Open question.

## Edge cases

| Input | Result |
| --- | --- |
| Two links in one message | Save both in order, one card each. Do not ask (decided). The same link twice (compared after tracking parameters are removed) is saved once. `pasted_text` applies to the first link only. If one link fails to store, the cards already saved are still returned with a `failed` list of the links that did not save. |
| A link followed by punctuation | Trailing `.` `,` `;` `:` `!` `?` are not part of the link. A closing `)` `]` `}` is removed only when the link has no matching opener. |
| A link inside a question | Treated as a link (regex wins). |
| Text with no link that is meant as a note | Treated as a question until a note path exists. A note path is wanted (decided); how the user marks a note is an open question. |
| Empty message | The server returns 400 with code `empty_message`. Nothing is saved. |
| Text with no link, in phase 1 | The app replies "I can only save links for now. Asking comes later." Nothing is sent to Claude. From phase 4 it is a question. |
| `note 42 for login tests` | Sets the reason of bookmark 42 to "for login tests" and marks it as the user's own. Reply: "Reason updated." |
| `note 999 text` (no such bookmark) | "I do not have a bookmark with that number." Nothing changes. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | A message with a URL never goes to the question path, and the reverse. Tested with code, no API call. |
| 2 | A readable page gives a card with all CI-03 parts. |
| 3 | An unreadable page gives the "Page not read" card and a null summary. |
| 4 | From phase 3: Undo returns the bookmark to its earlier folder. |
| 5 | After a reload, the earlier messages and cards are shown again. |
| 6 | `note <id> <text>` changes the reason, tested with code and no API call. |

## Tests

[route-set.md](test-cases/route-set.md), [hard-cases.md](test-cases/hard-cases.md).

## Open questions

- How the user marks a plain note, since CI-02 sends text without a link to the question path.
- How long Undo stays available (skipped for now; no time limit is set).
- Final message wording.

Decided: several links in one message are all saved, with no question asked.
