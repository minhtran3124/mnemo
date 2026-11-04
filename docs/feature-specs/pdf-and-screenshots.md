# PDFs and screenshots

Status: Draft v0.1 · Owner: KhoiTran · Phase: 4, 6

This file describes how a PDF or a screenshot is saved like a link.

## Purpose

You can upload a PDF or a screenshot and get a card. Supports F-10. Screenshots ship in phase 4. PDFs ship in phase 6.

## Scope

In: size and page check, big PDFs, screenshot rules.
Out: quotes in answers ([ask-and-answers.md](ask-and-answers.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| PS-01 | Code checks the page count and file size before the API call. |
| PS-02 | The limits are in `config.py`. Unverified: current API limits for pages and size. Check lesson 41 and the official docs in phase 6. |
| PS-03 | A big PDF: send only the first pages and the table of contents. |
| PS-04 | The card then says "summary from the first pages only". |
| PS-05 | A screenshot is sent as an image block. Type is `image`. |
| PS-06 | The summary uses only text that is clearly visible. |
| PS-07 | A screenshot has no URL. The URL field is optional. |
| PS-08 | The summary ignores screen clutter (reply box, icons). |
| PS-09 | The summary does not repeat a claim that the image does not support. |
| PS-10 | The card says "based on the visible text only" when text is cut (for example "Show more"). |

## Behavior and rules

### Big PDFs

Example from the plan: a 580-page, 14.6 MB book. Pages 1 to 3 were a printer cover layout, a title page and a copyright page. A summary from them alone would be thin or wrong. For a book, the useful parts are the table of contents and the description. So send the table of contents too. See [big-pdfs.md](../solutions/big-pdfs.md).

### Screenshot example: the @0xShoopy post

An X post screenshot about a PDF on building a skill library.

| Observation | Required behavior |
| --- | --- |
| Post says "Anthropic just dropped a 10-page PDF", but the page is headed "Field Notes", names @0xShoopy and says it is based on Anthropic's Agent Skills design | Do not state "Anthropic published this" as fact. Write "the post claims it" or leave it out. |
| Post ends with "Show more" | Card says "based on the visible text only". |
| No link | URL empty; optional field to add it. |
| Reply box and icons at the top | Ignored. |
| A PDF page shown inside an image, with small text | Use only text that is clearly readable. |

This is a hard check in the faithful-summary grader.

## Edge cases

| Case | Behavior |
| --- | --- |
| PDF over the size limit | Open question: refuse or send first pages. |
| Scanned PDF with no text | Open question. |
| Unreadable image | Link-only style card with null summary. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | An oversized PDF is checked by code before any API call. |
| 2 | The big PDF card says "first pages only". |
| 3 | The screenshot card does not say Anthropic published the PDF. |
| 4 | The screenshot card says "visible text only". |
| 5 | A screenshot can be saved without a URL. |

## Tests

[hard-cases.md](test-cases/hard-cases.md). Samples: [sample-links.md](../reference/sample-links.md).

## Open questions

- Real API limits for pages and size.
- Scanned PDFs.
- Where uploaded files are stored. See [storage.md](storage.md).
