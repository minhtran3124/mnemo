# Route set

Status: Draft v0.1 · Owner: KhoiTran · Phase: 3, 7

This file defines the Route set: 15 links with the expected type and the expected folder.

## Purpose

Score the type choice and the folder choice. Supports F-03 and F-13. Rules: [README.md](README.md). Folder rules: [folders.md](../folders.md).

## Format

Links come from [sample-links.md](../../reference/sample-links.md). The type column comes from the plan's type list ([data-model.md](../data-model.md)). The folder column stays blank until the owner picks her starter folders (open question in [folders.md](../folders.md)).

| id | link (from sample-links.md) | expected type | expected folder |
| --- | --- | --- | --- |
| R-01 |  |  |  |
| R-02 |  |  |  |
| R-03 |  |  |  |
| R-04 |  |  |  |
| R-05 |  |  |  |
| R-06 |  |  |  |
| R-07 |  |  |  |
| R-08 |  |  |  |
| R-09 |  |  |  |
| R-10 |  |  |  |
| R-11 |  |  |  |
| R-12 |  |  |  |
| R-13 |  |  |  |
| R-14 |  |  |  |
| R-15 |  |  |  |

## Scoring

| Check | Type | Rule |
| --- | --- | --- |
| Type match | Code | Equals the expected type. |
| Folder match | Code | Equals the expected folder. |
| Folder exists | Code | The returned folder is in the folder list or `Unsorted`. |
| Unsure goes to Unsorted | Review | For a link with no clear folder, `Unsorted` is a correct answer. Mark such rows with `Unsorted` as expected. |

Count wrong-folder cases and `Unsorted` cases separately. A wrong folder is worse than `Unsorted`, because it hides a bookmark.

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | The score is printed for type and for folder. |
| 2 | No link ends in a folder that does not exist. |
| 3 | The result is compared with at least 3 prompt versions (phase 3 done-check). |

## Open questions

- The starter folders.
- Which 15 links.
- Whether a `docs` or `other` expected type is used (D-013 is proposed).
