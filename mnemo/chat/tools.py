"""Read-only tools Claude uses to answer questions (F-07, AA tools).

Every read goes through store.py. This module never opens a file in the
data folder. The tool loop in ask.py turns a ToolError into a tool_result with
is_error.
"""

from typing import Any

from mnemo.core import config, store


class ToolError(ValueError):
    """A tool call has bad input. The loop sends this message back as is_error."""


def _searchable_text(bookmark: dict[str, Any]) -> str:
    """Title, summary, tags and reason, lowercased. A null summary is skipped."""
    parts = [
        bookmark.get("title") or "",
        bookmark.get("summary") or "",
        bookmark.get("reason") or "",
    ]
    tags = bookmark.get("tags")
    if isinstance(tags, list):
        parts.extend(str(tag) for tag in tags)
    return " ".join(parts).lower()


def search_bookmarks(query: str) -> list[dict[str, Any]]:
    """Find bookmarks with a keyword in the title, summary, tags or reason.

    Case-insensitive. Any word in the query may match. Returns at most
    config.SEARCH_RESULT_LIMIT results in saved order, with the fields Claude
    needs to choose an answer. An empty query is an error.
    """
    if not isinstance(query, str):
        raise ToolError("query must be a string")
    words = query.strip().lower().split()
    if not words:
        raise ToolError("query is empty")
    results: list[dict[str, Any]] = []
    for bookmark in store.list_bookmarks():
        haystack = _searchable_text(bookmark)
        if not any(word in haystack for word in words):
            continue
        results.append(
            {
                "id": bookmark["id"],
                "title": bookmark["title"],
                "type": bookmark["type"],
                "reason": bookmark["reason"],
                "reason_source": bookmark["reason_source"],
            }
        )
        if len(results) >= config.SEARCH_RESULT_LIMIT:
            break
    return results


def get_bookmark(bookmark_id: int) -> dict[str, Any]:
    """Return one bookmark by number, or raise ToolError when the id is unknown."""
    if not isinstance(bookmark_id, int) or isinstance(bookmark_id, bool):
        raise ToolError("id must be an integer")
    item = store.get_bookmark(bookmark_id)
    if item is None:
        raise ToolError(f"no bookmark with id {bookmark_id}")
    return item


def list_tags() -> list[dict[str, Any]]:
    """Return every tag once, sorted by name, with the number of bookmarks using it."""
    counts: dict[str, int] = {}
    for bookmark in store.list_bookmarks():
        tags = bookmark.get("tags")
        if not isinstance(tags, list):
            continue
        for tag in tags:
            name = str(tag)
            counts[name] = counts.get(name, 0) + 1
    return [{"tag": name, "count": counts[name]} for name in sorted(counts)]


TOOLS = [
    {
        "name": "search_bookmarks",
        "description": (
            "Search saved bookmarks by keyword in the title, summary, tags or reason. "
            "Use short keywords, not a full sentence. Returns at most "
            f"{config.SEARCH_RESULT_LIMIT} results with id, title, type and reason."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "One or more keywords, for example 'brotli'.",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_bookmark",
        "description": "Return one saved bookmark by its number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "The bookmark number shown by search results.",
                }
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_tags",
        "description": "List every saved tag once, sorted, with how many bookmarks use it.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
]

# The name used by the loop and by the spec.
TOOL_DEFINITIONS = TOOLS


def run_tool(name: str, arguments: Any) -> Any:
    """Call one tool by name. Bad input and unknown names raise ToolError."""
    if not isinstance(arguments, dict):
        raise ToolError("tool input must be an object")
    if name == "search_bookmarks":
        return search_bookmarks(arguments.get("query"))
    if name == "get_bookmark":
        return get_bookmark(arguments.get("id"))
    if name == "list_tags":
        return list_tags()
    raise ToolError(f"unknown tool: {name}")
