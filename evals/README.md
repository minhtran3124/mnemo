# Evals

## Expected answers

`expected.json` holds one expected answer for each page in `pages.json`: the type, 3 to 6 tags, 2 to 4 key facts taken from the saved text in `golden/`, whether the page is held out, whether it is a hard case, and `expect` (copied from `pages.json`). An unreadable page has no tags and no key facts. `golden.py` loads and checks the file.

The held-out pages are S-03, S-08, S-09, S-12 and S-13. Their URLs and key facts must never appear in `prompts/`. If the leak test fails, reword the key fact in `expected.json`, never the prompt or the test.

Entries marked draft are not reviewed; remove the mark after you read the page.
