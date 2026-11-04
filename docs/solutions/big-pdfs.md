# Solution: Big PDFs
Status: Draft v0.1 · Owner: KhoiTran · Phase: 6

How Mnemo handles a very large PDF.

## Problem
A book-size PDF may be over the API limits, and its first pages hold almost no useful content. A summary from them would be thin or wrong.

## Context
- Sample: the PDF book "AI-Ready PostgreSQL 18": 580 pages, 14.6 MB.
- Page 1 is a printer's cover layout with print marks and notes such as "Page Count: 580".
- Page 2 is the title page. Page 3 is the copyright page.
- Unverified: the current PDF page and size limits. The plan believes limits exist on both and has not checked the numbers. Check lesson 41 and the official docs (see [API notes](../reference/api-notes.md)).

## Solution
1. Before any API call, code checks the page count and file size.
2. If the PDF is within the limits (once verified), send it as a document block.
3. If it is over the limit, send only the first pages and the table of contents.
4. The card must say "summary from the first pages only".
5. For a book, look for the table of contents and the description, not page 1.
6. If no useful text is found, save as link only with an honest failure card.

Open question: how many first pages to send, and how to find the table of contents. The plan does not say.

## Why
- Product rule 2 and NF-04: do not claim more than the app saw.
- NF-02: cost limits. A 580-page file could cost a lot.
- Size check in code is exact and cheap.

## Where used
F-10 (PDF part), F-08. See [PDF and screenshots](../feature-specs/pdf-and-screenshots.md) and [phase 6 plan](../product/plans/phase-6-pdf-and-quotes.md).

## Tests
| Test | Expected |
| --- | --- |
| Save the 580-page PDF | Size check runs first; card says "first pages only" |
| Summary of the book | Does not describe print marks or the copyright text as the book content |
| Quote in an answer | The quote exists in the saved page text |
| PDF within limits | Normal summary |
