# Smoke Checklist
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

Run this short checklist after every phase. A smoke test is a quick check that the main paths still work. It takes about 20 minutes.

Use links from [sample links](../reference/sample-links.md). Mark each row Pass or Fail. If any row fails, fix it before you start the next phase.

| # | Check | How | Expected | Pass / Fail | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | Save a readable link | Paste one public article link in the chat | Card with title, type, 3 tags, a short summary, "Filed in" | | |
| 2 | Save an unreadable link | Paste a Slack message link | "Page not read" card, summary empty, Paste text field shown, no invented summary | | |
| 3 | Move (from phase 3) | Click Move on a card and pick another folder | The folder changes; the bookmark page shows it there | | |
| 4 | Undo (from phase 3) | Click Undo after a filing | The folder goes back; the count on the bookmark page matches | | |
| 5 | Search | Search a word from a saved title on the bookmark page | The bookmark appears, even if it is in another folder | | |
| 6 | Ask | Type a question about a saved link in your own words | Up to 3 bookmarks with a reason (or "guess") | | |
| 7 | Trick question | Ask about a topic you never saved | "Nothing found" and no invented bookmark | | |
| 8 | Phone width | Make the browser 390 px wide (or use your phone) | No sideways scroll; buttons easy to tap; text readable | | |
| 9 | No key in the browser source | Open the page, use "View source" and the network tab; search for `sk-` and for the word "key" | Your API key does not appear anywhere | | |
| 10 | Tracking parts | Paste a link ending with `?fbclid=abc` | The saved link has no `fbclid` | | |
| 11 | Unknown folder | Check the data after a save | The folder is one of your starter folders or Unsorted | | |
| 12 | Chat history | Save a link, then reload the page | The earlier messages and the card are shown again | | |
| 13 | Note | Type `note <id> for testing` for a saved bookmark | The reason changes and the bookmark page shows it as yours, not "guess" | | |

## Notes
- Rows 1 to 7 map to features F-01, F-02, F-03 and F-07. Rows 8 and 9 map to NF-05 and NF-01.
- Rows 6 and 7 apply from phase 4. Before phase 4, mark them "not built yet".
- Rows 12 and 13 apply from phase 1.
- Rows 3 and 4 (Move, Undo) apply from phase 3. In phases 1 and 2 mark them "not built yet".
- Row 11: Unsorted always exists (decision D-005, see [decision log](../process/decision-log.md)).
- Record the result in your [session note](../process/session-log-template.md).

## If a row fails
1. Write what you did and what you saw.
2. Do not start the next task.
3. Ask Claude Code to find the cause, with the note as input.
4. Run the whole checklist again, not only the failed row.
