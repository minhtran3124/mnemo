"""The Compact view: a third choice next to Cards and Ledger (#112)."""

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import store

FAKE_KEY = "sk-ant-fake-key-for-tests"
ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


def rule_body(css: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert match, f"no rule for `{selector}` in bookmarks.css"
    return match.group(1)


def test_page_offers_three_views_including_compact(client):
    html = client.get("/bookmarks").text

    assert html.count('class="view-btn"') == 3
    for view, label in (
        ("ledger", "Ledger"),
        ("cards", "Cards"),
        ("compact", "Compact"),
    ):
        assert f'data-view="{view}"' in html
        assert f">{label}</button>" in html

    script = client.get("/static/js/view-switcher.js").text
    assert 'compact: "view-compact"' in script


def test_compact_is_stored_and_read_back_on_reload(client):
    script = client.get("/static/js/view-switcher.js").text

    assert "localStorage.getItem(STORAGE_KEY)" in script
    assert "localStorage.setItem(STORAGE_KEY, view)" in script
    assert "CLASSES[value] ? value : DEFAULT_VIEW" in script
    assert "CLASSES[view]" in script
    assert "CLASSES.cards, CLASSES.ledger, CLASSES.compact" in script


def test_compact_rows_are_one_line_and_hide_the_long_parts():
    css = (WEB / "css" / "bookmarks.css").read_text(encoding="utf-8")

    row = rule_body(css, ".bm-list.view-compact .bm-row")
    assert re.search(r"flex-direction:\s*row", row)
    assert re.search(r"flex-wrap:\s*nowrap", row)

    main = rule_body(css, ".bm-list.view-compact .bm-main")
    assert re.search(r"display:\s*flex", main)
    assert re.search(r"flex-wrap:\s*nowrap", main)

    hide = re.search(r"(\.bm-list\.view-compact \.bm-filed[^{]*)\{([^}]*)\}", css)
    assert hide, "no rule hides the long parts in Compact"
    selectors, body = hide.group(1), hide.group(2)
    assert re.search(r"display:\s*none", body)
    for name in ("bm-filed", "bm-summary", "bm-tags", "bm-actions"):
        assert f".bm-list.view-compact .{name}" in selectors


def test_cards_and_ledger_still_work(client):
    html = client.get("/bookmarks").text

    assert 'data-view="ledger"' in html
    assert 'data-view="cards"' in html

    script = client.get("/static/js/view-switcher.js").text
    assert 'cards: "view-cards"' in script
    assert 'ledger: "view-ledger"' in script
    assert 'DEFAULT_VIEW = "ledger"' in script

    css = (WEB / "css" / "bookmarks.css").read_text(encoding="utf-8")
    assert ".bm-list.view-cards" in css
    assert ".bm-list.view-ledger" in css
