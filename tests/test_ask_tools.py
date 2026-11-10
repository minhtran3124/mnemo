"""The read-only ask tools (ticket #117, F-07). No network."""

from pathlib import Path
from typing import Any

import pytest

import config
import store
import tools


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    return tmp_path


def seed(**overrides: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "url": "https://example.com/a",
        "url_clean": "https://example.com/a",
        "type": "article",
        "title": "An article",
        "page_status": "ok",
        "summary": "A short summary.",
        "tags": ["python", "testing", "tools"],
        "reason": "",
        "reason_source": "guess",
        "folder": None,
        "opened_count": 0,
    }
    record.update(overrides)
    return store.add_bookmark(record, page_text="page body")


def test_search_finds_a_title_word_ignoring_case():
    bookmark = seed(title="Brotli compression notes")

    found = tools.search_bookmarks("brotli")

    assert [item["id"] for item in found] == [bookmark["id"]]
    assert found[0]["title"] == "Brotli compression notes"
    assert set(found[0]) == {"id", "title", "type", "reason", "reason_source"}


def test_search_finds_summary_tag_and_reason():
    by_summary = seed(title="One", summary="A guide to WebSocket performance.")
    by_tag = seed(title="Two", tags=["brotli", "python", "web"])
    by_reason = seed(title="Three", reason="Useful for the login tests")

    assert [item["id"] for item in tools.search_bookmarks("websocket")] == [
        by_summary["id"]
    ]
    assert [item["id"] for item in tools.search_bookmarks("brotli")] == [by_tag["id"]]
    assert [item["id"] for item in tools.search_bookmarks("LOGIN")] == [by_reason["id"]]


def test_search_limit_and_empty_result():
    for index in range(12):
        seed(title=f"Needle {index}", url=f"https://example.com/{index}")

    found = tools.search_bookmarks("needle")

    assert len(found) == config.SEARCH_RESULT_LIMIT
    assert tools.search_bookmarks("nothing-matches-this") == []


def test_get_bookmark_returns_the_record_and_unknown_id_errors():
    bookmark = seed(title="Known")

    assert tools.get_bookmark(bookmark["id"])["title"] == "Known"
    with pytest.raises(tools.ToolError, match="no bookmark with id 99"):
        tools.get_bookmark(99)


def test_list_tags_returns_each_tag_once_sorted_with_counts():
    seed(tags=["python", "ai", "web"])
    seed(tags=["ai", "testing", "web"])

    assert tools.list_tags() == [
        {"tag": "ai", "count": 2},
        {"tag": "python", "count": 1},
        {"tag": "testing", "count": 1},
        {"tag": "web", "count": 2},
    ]


def test_empty_query_and_bad_id_raise_clear_errors():
    with pytest.raises(tools.ToolError, match="query is empty"):
        tools.search_bookmarks("   ")
    with pytest.raises(tools.ToolError, match="query must be a string"):
        tools.search_bookmarks(None)  # type: ignore[arg-type]
    with pytest.raises(tools.ToolError, match="id must be an integer"):
        tools.get_bookmark("1")  # type: ignore[arg-type]
    with pytest.raises(tools.ToolError, match="id must be an integer"):
        tools.get_bookmark(True)


def test_link_only_bookmark_searches_without_a_summary():
    bookmark = seed(
        title="Bare link",
        page_status="unreadable",
        summary=None,
        tags=["python", "bare"],
        reason="Saved for later",
    )

    assert [item["id"] for item in tools.search_bookmarks("bare")] == [bookmark["id"]]
    assert [item["id"] for item in tools.search_bookmarks("later")] == [bookmark["id"]]


def test_tools_only_read_through_store(monkeypatch):
    calls: list[str] = []
    real = store.list_bookmarks

    def spy(*args, **kwargs):
        calls.append("list_bookmarks")
        return real(*args, **kwargs)

    monkeypatch.setattr(store, "list_bookmarks", spy)
    seed(title="A stored title")

    tools.search_bookmarks("stored")
    tools.list_tags()

    assert calls == ["list_bookmarks", "list_bookmarks"]
    source = Path(tools.__file__).read_text(encoding="utf-8")
    assert "store." in source
    assert "open(" not in source
    assert "Path(" not in source
    assert "data/" not in source
