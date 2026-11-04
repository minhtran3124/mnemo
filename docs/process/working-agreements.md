# Working Agreements
Status: Draft v0.1 · Owner: KhoiTran · Phase: all

These are the rules for how you and Claude Code work together on Mnemo. They keep each session small and safe.

| # | Agreement | Why |
| --- | --- | --- |
| 1 | A session is about 30 minutes. | The plan is built on 30-minute sessions. |
| 2 | One change at a time. | If a score or a screen gets worse, you know which change caused it. |
| 3 | Claude Code writes the code. You review it, run it, and judge the result. | You decide; the tool types. Lessons 58 to 60 teach this. |
| 4 | Plan before code. Ask Claude Code for a short plan first and read it. | A wrong plan is cheaper to fix than wrong code. |
| 5 | Small commits. One commit per working change, with a clear message. | You can go back to the last good state. |
| 6 | Ask when unsure. If a fact is not in the docs, write it as an open question. | No invented facts. See [open questions](../research/open-questions.md). |
| 7 | Never print or paste the API key. | See [git and secrets](git-and-secrets.md). |
| 8 | End each session with a short note. | The next session starts fast. See [session log template](session-log-template.md). |
| 9 | Do not start the next phase until the current check passes. | Each phase ends with something you can do and a check you run. |
| 10 | Public links only while building (D-018). | Page text goes to the API. |

## How a session runs
1. Read the last session note (2 minutes).
2. Pick one task from the current phase plan in [phases overview](../product/phases-overview.md).
3. Ask Claude Code for a plan. Read it. Change it if needed.
4. Let Claude Code write the code.
5. Review the change. Run it. Try one sample link from [sample links](../reference/sample-links.md).
6. Commit if it works.
7. Write the session note.

## How to review code if you do not write code every day
You are a QA professional. Review like a tester.
- Run it with a good input and a bad input.
- Check that the key is not in any new file.
- Check that an unreadable page gives no summary.
- Ask Claude Code to explain any part you do not understand, in simple words.
- If you cannot explain what a change does, do not commit it yet.

## When time runs short
Cut in the order given in the [roadmap](../product/roadmap.md). Never cut phases 0 to 4, phase A, or the eval.

## Open questions
- Open question: how many sessions per week you can do. The plan assumes about 3.
