# Solution: Safe Auto-Filing
Status: Draft v0.1 · Owner: KhoiTran · Phase: 3

How Mnemo files a bookmark into a folder without hiding it (feature F-03, decision D-005).

## Problem
You asked the app to save into the correct place on its own. A wrong folder hides a bookmark. A model can also invent a folder name.

## Context
- You write 5 or 6 starter folders yourself. Examples only: Dev tools, Articles to read, AI and agents, Work, Fun, Unsorted.
- In phase 1 every bookmark goes to Unsorted and the list is grouped by type. Real folders start in phase 3.
- Product rule 3: you stay in control. The app never moves or deletes anything alone.

## Solution
1. Claude chooses one folder from the folders that already exist, or Unsorted. It does not invent a folder during a save.
2. When Claude is not sure, it must choose Unsorted.
3. Code checks that the folder name exists. An unknown folder name is rejected.
4. The card shows "Filed in: <folder>" with Move and Undo, always visible.
5. Search ignores folders, so a bookmark in the wrong folder can still be found.
6. New folders are proposed only for the whole list, in phase 7. You accept or reject each one. Nothing moves without your yes.
7. Code checks that every bookmark has exactly one folder.

Open question: the `folder` field is null until accepted or filed (data model). How this fits with filing at save time needs a final wording in [folders](../feature-specs/folders.md).

## Why
- Unsorted does not hide a bookmark; a wrong folder does.
- Code rules are exact; model rules can fail.
- Filing accuracy is measured on the Route set (15 links) in the eval.

## Where used
F-03, F-13. See [classification and filing](../feature-specs/classification-and-filing.md) and [phase 3 plan](../product/plans/phase-3-trust-and-filing.md).

## Tests
| Test | Expected |
| --- | --- |
| Model returns a folder not in your list | Rejected; bookmark goes to Unsorted |
| Unclear link | Unsorted |
| Click Undo | Previous folder restored |
| Search for a bookmark in a different folder | Found |
| Route set | Folder choice scored in the eval |
