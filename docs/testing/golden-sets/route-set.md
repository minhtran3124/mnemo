# Route set

Status: Draft v0.1 · Owner: KhoiTran · Phase: 3, 7

This file defines the Route set: 15 links with the expected type and the expected folder.

## Purpose

Score the type choice and the folder choice. Supports F-03 and F-13. Rules: [README.md](README.md). Folder rules: [folders.md](../../feature-specs/folders.md).

## Format

Links come from [sample-links.md](../../reference/sample-links.md); the last row is the phase 1 login page that tests an unreadable page. Each row also has a page in the Save set, so the eval uses the saved page text and does not fetch today's web. The starter folders are Work, Learning, Reference, Personal and Ideas; `Unsorted` means "not sure". Every expected folder below is a **draft** until the owner reads the page, like `evals/expected.json`.

| id | save page | sample link | expected type | expected folder | draft |
| --- | --- | --- | --- | --- | --- |
| R-01 | S-01 | #1, X post by Addy Osmani | article | Learning | yes |
| R-02 | S-02 | #2, Pocket alternatives guide | article | Learning | yes |
| R-03 | S-03 | #3, Airtable home | tool | Work | yes |
| R-04 | S-04 | #4, Hugging Face skills article | article | Learning | yes |
| R-05 | S-05 | #7, maple-font repo | github_repo | Reference | yes |
| R-06 | S-06 | #8, ai_agents_az repo | github_repo | Learning | yes |
| R-07 | S-07 | #9, colorfigures tool page | tool | Ideas | yes |
| R-08 | S-08 | #10, YouTube video | video_page | Unsorted | yes |
| R-09 | S-09 | #14, WeAreDevelopers videos index | video_page | Unsorted | yes |
| R-10 | S-10 | #16, Airtable API introduction | tool | Unsorted | yes |
| R-11 | S-11 | #17, Claude Code Game Studios repo | github_repo | Learning | yes |
| R-12 | S-12 | #19, arXiv paper | article | Learning | yes |
| R-13 | S-13 | #20, Uber AI code cleanup | article | Learning | yes |
| R-14 | S-14 | #21, agent spec article | article | Ideas | yes |
| R-15 | S-15 | phase 1 login page (unreadable) | tool | Unsorted | yes |

## Scoring

| Check | Type | Rule |
| --- | --- | --- |
| Type match | Code | Equals the expected type. |
| Folder match | Code | Equals the expected folder. `Unsorted` is stored as a null folder. |
| Folder exists | Code | The returned folder is a starter folder or `Unsorted`. |
| Unsure goes to Unsorted | Review | For a link with no clear folder, `Unsorted` is a correct answer. Mark such rows with `Unsorted` as expected. |

Count wrong-folder cases and `Unsorted` cases separately. A wrong folder is worse than `Unsorted`, because it hides a bookmark. A made-up folder name is rejected by code and counts as a miss in the folder score.

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | The score is printed for type and for folder. |
| 2 | No link ends in a folder that does not exist. |
| 3 | The result is compared with at least 3 prompt versions (phase 3 done-check). |

## Open questions

- Whether a `docs` or `other` expected type is used (D-013 is proposed).
- Whether the owner accepts each draft type and folder.
