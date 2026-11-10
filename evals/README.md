# Evals

## Expected answers

`expected.json` holds one expected answer for each page in `pages.json`: the type, 3 to 6 tags, 2 to 4 key facts taken from the saved text in `golden/`, the folder in `expected_folder` (a starter folder or `Unsorted`), whether the page is held out, whether it is a hard case, and `expect` (copied from `pages.json`). An unreadable page has no tags and no key facts. `golden.py` loads and checks the file.

The 15 pages are the Route set. Each `expected_folder` says where that link belongs; a made-up folder is not allowed. `Unsorted` is stored as a null folder, so a null folder in a record matches `Unsorted`.

The held-out pages are S-03, S-08, S-09, S-12 and S-13. Their URLs and key facts must never appear in `prompts/`. If the leak test fails, reword the key fact in `expected.json`, never the prompt or the test.

Entries with `"draft": true` are not reviewed; set it to `false` after you read the page. The key is required in every entry.

## Run the eval

```
uv run python -m evals.run_eval --run-id <id> --prompt-version <name>
```

It previews every page in `pages.json` (nothing is written to `data/`), prints save quality, honesty, find rate and folder choice as four separate scores, and appends one row to `results/runs.csv`. See `docs/process/eval-process.md`.

The folder choice score is the share of the 15 Route rows where the model's folder equals `expected_folder`. The eval reads the raw model folder, not the stored record, so a made-up name that code would reject still counts as a miss. Older rows in `runs.csv` have an empty `folder_score`; they are left as they were.
