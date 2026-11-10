# Ask and answers

Status: Draft v0.1 · Owner: KhoiTran · Phase: 4, 6

This file describes how you ask in plain words and how answers show their sources.

## Purpose

You type a question and get up to 3 links, each with the reason you saved it. Supports F-07 and F-08.

## Scope

In: tool loop, tools, result limit, "nothing found", sources, quotes.
Out: the better search of phase 5 (see [search-no-embeddings.md](search-no-embeddings.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| AA-01 | A message without a web address is a question ([chat-and-intent.md](chat-and-intent.md)). |
| AA-02 | An answer has at most 3 bookmarks. |
| AA-03 | Each result shows the bookmark number, title, type and the reason you saved it. A guessed reason is marked "guess". |
| AA-04 | If nothing fits, the answer is "nothing found". |
| AA-05 | Every answer names the bookmarks it used (F-08). |
| AA-06 | Code checks that every bookmark number in an answer exists. |
| AA-07 | Later (phase 6), an answer shows a quote. Code checks the quote exists in the saved page text. |
| AA-08 | The final answer is streamed to the screen. |

## Tools

| Tool | What it does |
| --- | --- |
| `search_bookmarks` | Keyword search over title, summary, tags and reason (phase 4). Replaced by the better retriever in phase 5. |
| `get_bookmark` | Returns one bookmark by number. |
| `list_tags` | Returns all tags. |

### Built in phase 4

`mnemo/chat/tools.py` holds both the tool definitions sent to Claude and the functions behind them. Every read goes through `mnemo/core/store.py`; it never opens a file in the data folder.

- `search_bookmarks(query)` ignores case and searches title, summary, tags and reason. A link-only bookmark has no summary, so it is searched by the other three. It returns at most `config.SEARCH_RESULT_LIMIT` (10) results, in saved order, as `id`, `title`, `type`, `reason` and `reason_source`.
- `get_bookmark(id)` returns the record for a number, or a clear error when the number is unknown.
- `list_tags()` returns each tag once, sorted, with the number of bookmarks using it.
- Bad input (an empty query, a non-integer id) raises `ToolError` with a readable message. The tool loop sends that message back with `is_error`, so Claude can react.

### Tool loop

`mnemo/chat/ask.py` has `run_ask(question)`. It sends the question and the `mnemo/chat/tools.py` definitions to Claude, then continues while `stop_reason` is `tool_use`. Every `tool_use` block gets one `tool_result` with the same `tool_use_id`, in one user message. A tool that raises or an unknown tool name gets `is_error: true` with the message, so Claude can try another tool or say it could not search.

The loop stops after `config.ASK_MAX_ROUNDS` (6) rounds and returns an error result instead of looping forever. It returns an `AskResult` with the final text, every tool call it made, and an optional error code. Each Claude call logs its token counts like the other calls.

### Route in the chat

`POST /api/chat` sends a message with no link (and not a `note <id> <text>` command) to `ask.run_ask`. The reply is `{"kind": "answer", "text": ..., "bookmarks": [...]}`.

Claude is asked to name each bookmark as `#<id>`. The server reads those numbers, fetches the stored records and keeps at most `config.ASK_ANSWER_LIMIT` (3). Each result has `id`, `title`, `type`, `reason` and `reason_source`, so the page can mark a guessed reason. When no bookmark survives, the text is "nothing found" and the list is empty. The question and the answer are saved to chat history, with the bookmark ids on the app message. A Claude error returns the usual JSON 500.




Tools return clear errors. When a tool fails, the loop sends the error back with `is_error` set, so Claude can react.

## Behavior and rules

1. The question goes to Claude with the tool definitions.
2. While Claude's `stop_reason` is `tool_use`, the server runs each requested tool and sends back a result for every call.
3. When Claude is done, the final answer is streamed.
4. Code checks the numbers in the answer (AA-06).

- Answer example from the plan: "2 bookmarks fit." followed by a number, type, title and "Why you saved it".
- Never more than three results at once.
- If a question has no good match in your list, the right result is "nothing found" and no bookmark. The 3 trick questions test this.

## Edge cases

| Case | Behavior |
| --- | --- |
| A tool call fails | Error sent back; Claude may retry or say it could not search. |
| Claude names a bookmark number that does not exist | Code removes it or the check fails. |
| Empty list | "nothing found". |
| Question about a private bookmark (F-19) | Only link and reason can match. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | 15 questions run; the right bookmark is in the top 3. Target: set after first baseline. |
| 2 | 3 trick questions return "nothing found". |
| 3 | Every tool call has a result. |
| 4 | All cited numbers exist. |
| 5 | A grader says yes or no: is the answer supported by the bookmarks it cites? |
| 6 | (phase 6) Every quote is found in the page text. |

## Tests

[ask-golden-set.md](../testing/golden-sets/ask-golden-set.md).

## Open questions

- Quote format in the answer.
- Tone of the "nothing found" message.
