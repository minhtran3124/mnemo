# Folders

Status: Draft v0.1 · Owner: KhoiTran · Phase: 3, 7

This file holds the rules for auto-filing (D-005), because a wrong folder can hide a bookmark.

## Purpose

You want the app to file links on its own. That is fine only if every filing is visible and easy to undo. Supports F-03 and F-13. See also the plan note on safe filing in [safe-auto-filing.md](../solutions/safe-auto-filing.md).

## Scope

In: starter folders, filing rules, Unsorted, Move, Undo, code validation, folder proposals.
Out: how Claude is prompted (see [classification-and-filing.md](classification-and-filing.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| FO-01 | Claude chooses only from existing folders or `Unsorted`. It never invents a folder during a save. |
| FO-02 | When Claude is not sure, it must choose `Unsorted`. |
| FO-03 | Code checks that the folder name exists. An unknown name is rejected and the bookmark goes to `Unsorted`. |
| FO-04 | `Unsorted` always exists and cannot be deleted. |
| FO-05 | Move and Undo are always visible on the card and on each row. |
| FO-06 | Search ignores folders, so a wrongly filed bookmark can still be found. |
| FO-07 | In phase 1, every bookmark goes to `Unsorted`. Real folders start in phase 3. |
| FO-08 | In phase 7, Claude may propose new folders for the whole list. Nothing moves without your yes. |
| FO-09 | After a proposal is accepted, code checks that every bookmark has exactly one folder. |

## Behavior and rules

### Starter folders

The five starter folders live in `config.STARTER_FOLDERS`: Work, Learning, Reference, Personal, Ideas. `config.UNSORTED` is `Unsorted`. Code accepts only these names, with exact letter case (`config.is_allowed_folder`). `Unsorted` is stored as a null folder.

### Why Unsorted

A wrong folder hides a bookmark. `Unsorted` does not. So doubt always goes to `Unsorted`.

### Move

Move shows the list of existing folders. You pick one. The change is saved at once and logged.

### Undo

Undo puts the bookmark back to the folder it had before the last filing or Move. Open question: how many steps back Undo can go. Start with one step.

### Folder proposals (phase 7)

1. Claude reads the list and proposes a folder tree.
2. You see each proposed folder. You accept, change or reject each one.
3. Only accepted folders are created. Only then do bookmarks move, and only with your yes.
4. A table compares four ways to build the save step: single prompt, chain, parallel sub-tasks, review step. This is an eval task, see the phase 7 plan.

## Edge cases

| Case | Behavior |
| --- | --- |
| Claude returns a folder that does not exist | Rejected. Filed in `Unsorted`. Counted in the log. |
| You rename or delete a folder that holds bookmarks | Open question. Safe default: move them to `Unsorted`. |
| Two folders fit | Claude picks the best one or `Unsorted`. |
| Private link (proposed F-19) | Open question: filed to `Unsorted` since no API call is made. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | A test that feeds an unknown folder name ends with `Unsorted`. |
| 2 | Move and Undo work on 10 real saves. |
| 3 | Every bookmark has one folder after a proposal is accepted. |
| 4 | Search finds a bookmark whatever its folder. |
| 5 | Route set score is recorded for the folder choice. |

## Tests

[route-set.md](test-cases/route-set.md).

## Open questions

- Undo depth.
- What happens to bookmarks when a folder is deleted.
