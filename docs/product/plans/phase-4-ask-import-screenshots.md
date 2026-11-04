# Phase 4: Ask, Import and Screenshots
Status: Draft v0.1 · Owner: KhoiTran · Phase: 4

Add questions in the chat, import of your old pile, and screenshots. After this phase, run the 2-week test.

## Goal
F-06 (import), F-07 (ask), F-08 (sources, first part), F-10 (screenshots).

## You can now
Ask questions in the chat, import your old pile, save screenshots.

## Sessions and lessons
4 sessions. Lessons 7, 20-28, 40.

## Inputs
Phase 3 done. 15 questions you wrote plus 3 trick questions: [ask golden set](../../feature-specs/test-cases/ask-golden-set.md). A browser bookmarks export and some pasted text from Slack or notes.

## Tasks
1. Write tools `search_bookmarks` (keyword search over title, summary, tags, reason), `get_bookmark`, `list_tags`, all through `store.py`. Give clear errors.
2. Write the tool loop: continue while `stop_reason` is `tool_use`. Answer every tool call; send `is_error` on failure.
3. Route in the chat: URL pattern means save, otherwise ask (D-004).
4. Stream the final answer: up to 3 bookmarks with reasons; say "nothing found" when nothing fits.
5. Show sources: each answer names the bookmark numbers used (F-08). Code checks that every number exists.
6. Add `open <id>`: opens the link and logs it (needed for the "Do I come back?" measure).
7. Run the ask eval: 15 questions and 3 trick questions.
8. Screenshots: add an image block to the save flow. Card says "based on the visible text only"; link is empty with an optional field; ignore clutter.
9. Import page: read the browser bookmarks file. Show link count and a cost estimate first.
10. Import: accept pasted text (Slack, notes, messages) and find links in it. Slack links themselves cannot be read; the chat accepts pasted message text. See [Slack and login pages](../../solutions/slack-and-login-pages.md).
11. Import in batches of about 20 so you can stop. Mark imported records `source: import` (proposed field).
12. Import test: 40 old links; expect some unreadable pages.
13. Start the 2-week test: [two-week user test](../../manual-testing/two-week-user-test.md). This is decision point 2.

## Done when
- [ ] 15 questions and 3 trick questions run; trick questions return "nothing found".
- [ ] Every tool call gets a result.
- [ ] Browser bookmarks import in batches; pasted Slack text gives links.
- [ ] A screenshot saves as type `image` and the card does not repeat claims the image does not support.
- [ ] The success table is filled after 2 weeks.

## Risks
You stop using it; unreadable old links. See [risk review](../../reviews/risk-review.md).

## If time runs short
Cut screenshots (move to a later phase). Do not cut ask or import.

## Links to specs
[ask and answers](../../feature-specs/ask-and-answers.md) · [import](../../feature-specs/import.md) · [PDF and screenshots](../../feature-specs/pdf-and-screenshots.md) · [chat and intent](../../feature-specs/chat-and-intent.md) · [ask golden set](../../feature-specs/test-cases/ask-golden-set.md)
