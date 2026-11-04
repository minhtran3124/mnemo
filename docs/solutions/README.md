# Solutions
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

A solution note records how Mnemo handles one hard case, so you do not solve the same problem twice.

## What a solution note is
A short file about one problem, the choice made, and how to test it. It uses facts from the plan's samples and decisions. If a fact is not in the plan, it is marked Open question or Unverified.

## Template

| Section | What to write |
| --- | --- |
| Problem | What goes wrong, in one or two sentences |
| Context | The sample or case that shows it |
| Solution | What the app does, in steps |
| Why | The reason, linked to a rule, requirement or decision |
| Where used | Features, specs and phases |
| Tests | How a person or code checks it |

## Notes

| Note | Problem |
| --- | --- |
| [Honest failure](honest-failure.md) | A page cannot be read |
| [URL cleaning](url-cleaning.md) | Tracking parts make the same link look different |
| [Slack and login pages](slack-and-login-pages.md) | Pages that need a sign-in |
| [Big PDFs](big-pdfs.md) | A book-size PDF with a useless first page |
| [Safe auto-filing](safe-auto-filing.md) | AI filing can hide a bookmark |

## Rules for writing a note
- Plain English, short sentences.
- No calendar dates.
- Link to the spec that holds the rule. Do not copy long rules.
- Add a note when a case took more than one session to solve, or when it will come back.

Hard cases are listed in [hard cases](../feature-specs/test-cases/hard-cases.md). Sample links are in [sample links](../reference/sample-links.md).
