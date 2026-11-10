# Phase 6: PDF and Quotes
Status: Draft v0.1 · Owner: KhoiTran · Phase: 6

Save PDFs and show exact quotes in answers.

## Goal
F-10 (PDF) and F-08 (quotes).

## You can now
Get quotes, and save PDFs.

## Sessions and lessons
2 sessions. Lessons 41, 42.

## Inputs
Phase 4 done. One small PDF and the 580-page book from the [hard cases](../../testing/golden-sets/hard-cases.md).

## Tasks
1. Check the current PDF page and size limits in lesson 41 and the official docs. They are Unverified; do not trust the numbers in this plan.
2. Add a size check in code before the API call (page count and file size).
3. Send a small PDF as a document block. Save it as type `pdf`.
4. For a big PDF, send only the first pages and the table of contents. The card must say "summary from the first pages only". See [big PDFs](../../solutions/big-pdfs.md).
5. Turn on citations in answers.
6. Add a code check: every quoted sentence exists in the saved page text (`data/pages/<id>.txt`).
7. Test with a quote that does not exist; the check must fail it.

## Done when
- [ ] A small PDF is saved and gets a card.
- [ ] The 580-page PDF does not crash and the card says first pages only.
- [ ] An answer shows a quote and code confirms it is in the page text.
- [ ] A made-up quote is rejected.

## Risks
Limits unknown; first pages of a book hold little content (cover layout, copyright). See [risk review](../../research/risk-review.md).

## If time runs short
Cut quotes, keep PDF. This phase is fifth in the cut order.

## Links to specs
[PDF and screenshots](../../feature-specs/pdf-and-screenshots.md) · [ask and answers](../../feature-specs/ask-and-answers.md) · [page reading](../../feature-specs/page-reading.md) · [hard cases](../../testing/golden-sets/hard-cases.md)
