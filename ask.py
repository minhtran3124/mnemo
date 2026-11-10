"""Answer a question with a tool loop over the saved bookmarks (F-07).

The loop sends the question and the tool definitions to Claude, runs every
requested tool, and sends one tool_result back for each tool_use block. A tool
failure or an unknown tool becomes a tool_result with is_error, so Claude can
react. A round cap stops a loop that never ends. No network call is made here;
client.py owns the SDK.
"""

import json
from dataclasses import dataclass, field
from typing import Any

import client
import config
import tools

ASK_SYSTEM = (
    "Answer the user's question from the saved bookmarks. Use the tools to look "
    "them up. Use at most 3 bookmarks in one answer. Name each bookmark you use "
    'as #<number>, for example #3. If nothing fits, say "nothing found". Never '
    "invent a bookmark."
)


class AskError(ValueError):
    """The question cannot be sent. The caller shows the message."""


@dataclass
class AskResult:
    """The final text and every tool call the loop made."""

    text: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


def _as_dict(block: Any) -> dict[str, Any]:
    """Turn an SDK content block (or a fake) into a plain dict."""
    if isinstance(block, dict):
        return block
    dumped = getattr(block, "model_dump", None)
    if callable(dumped):
        return dumped()
    kind = getattr(block, "type", "unknown")
    if kind == "text":
        return {"type": "text", "text": getattr(block, "text", "")}
    if kind == "tool_use":
        return {
            "type": "tool_use",
            "id": getattr(block, "id", None),
            "name": getattr(block, "name", None),
            "input": getattr(block, "input", {}),
        }
    return {"type": kind}


def _text_of(blocks: list[dict[str, Any]]) -> str:
    return "".join(
        block.get("text", "") for block in blocks if block.get("type") == "text"
    )


def _tool_results(
    blocks: list[dict[str, Any]], calls: list[dict[str, Any]]
) -> list[dict]:
    """Run every tool_use block and return one tool_result for each, in order."""
    results: list[dict] = []
    for block in blocks:
        if block.get("type") != "tool_use":
            continue
        name = block.get("name")
        arguments = block.get("input")
        calls.append({"name": name, "input": arguments})
        try:
            output = tools.run_tool(name, arguments)
        except Exception as exc:  # noqa: BLE001 - a tool failure must not break the loop
            # A tool must never break the loop. Claude gets the message and can
            # try another tool or say it could not search.
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.get("id"),
                    "content": str(exc),
                    "is_error": True,
                }
            )
        else:
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.get("id"),
                    "content": json.dumps(output, ensure_ascii=False),
                }
            )
    return results


def run_ask(question: str) -> AskResult:
    """Answer one question, running tools until Claude stops or the round cap hits."""
    if not isinstance(question, str) or not question.strip():
        raise AskError("question is empty")

    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    calls: list[dict[str, Any]] = []
    for _ in range(config.ASK_MAX_ROUNDS):
        response = client.create_message(
            messages, tools=tools.TOOL_DEFINITIONS, system=ASK_SYSTEM
        )
        blocks = [_as_dict(block) for block in response.content]
        messages.append({"role": "assistant", "content": blocks})
        if response.stop_reason != "tool_use":
            return AskResult(text=_text_of(blocks), tool_calls=calls)
        messages.append({"role": "user", "content": _tool_results(blocks, calls)})

    return AskResult(
        text="I could not finish the search. Please try a narrower question.",
        tool_calls=calls,
        error="too_many_rounds",
    )
