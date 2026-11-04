# Session Log Template
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

Use this short note at the end of every 30-minute session. It lets you and Claude Code start the next session fast. Do not write calendar dates; use the session number.

## Template
Copy this into a new note.

```markdown
## Session <number> · Phase <0-10, A, B or C>

**Goal:** one sentence.
**Done:** what works now (one or two lines).
**Checked by:** code check / eval / manual (which sample links).
**Not done or broken:** one or two lines.
**Decisions:** any new decision (use a D- number if it is big).
**Open questions:** new questions for the docs.
**Cost note:** rough API use, if you know it.
**Next task:** the one task for the next session.
```

## Example (invented, for format only)
```markdown
## Session 4 · Phase 1

**Goal:** show a card for a readable link.
**Done:** the chat page returns a card for a GitHub link.
**Checked by:** manual, 2 sample links.
**Not done or broken:** the unreadable link shows an error.
**Decisions:** none.
**Open questions:** none.
**Cost note:** low.
**Next task:** show the "Page not read" card.
```

## The line for progress-log.md
Your Learning Claude project asks for one line to add to `progress-log.md` at the end of a session. Use this form:

```text
Session <number> · Phase <x> · <done in five words> · next: <task>
```

## Rules
- Keep it under 10 lines.
- Write facts, not feelings.
- If you changed a plan or a spec, say which file.

Related: [working agreements](working-agreements.md), [definition of done](definition-of-done.md).
