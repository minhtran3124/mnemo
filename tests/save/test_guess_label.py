"""A reason Claude guessed carries a "guess" label until the user edits it (#111)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mnemo.core import store

FAKE_KEY = "sk-ant-fake-key-for-tests"
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    from mnemo.api import server

    return TestClient(server.app)


def seed(**overrides):
    record = {
        "url": "https://example.com/a",
        "url_clean": "https://example.com/a",
        "type": "article",
        "title": "An article",
        "page_status": "ok",
        "summary": "A short summary.",
        "tags": ["testing", "login", "python"],
        "reason": "Looks useful for login work",
        "reason_source": "guess",
        "folder": None,
        "opened_count": 0,
    }
    record.update(overrides)
    return store.add_bookmark(record, page_text="page body")


def test_bookmark_row_with_a_guessed_reason_shows_the_label(client):
    seed(reason="Looks useful for login work", reason_source="guess")

    text = client.get("/bookmarks").text

    assert "Looks useful for login work" in text
    assert '<span class="badge">guess</span>' in text


def test_chat_card_wires_the_label_to_a_guessed_reason():
    script = (ROOT / "mnemo" / "api" / "web" / "js" / "chat.js").read_text(
        encoding="utf-8"
    )

    assert 'record.reason_source === "guess"' in script
    assert 'why.appendChild(el("span", "flag", "guess"))' in script
    assert 'why.appendChild(el("strong", null, "Why you saved it:"))' in script


def test_user_reason_has_no_label_and_note_clears_it_after_reload(client):
    seed(reason="Looks useful for login work", reason_source="guess")

    guessed = client.get("/bookmarks").text
    assert "Looks useful for login work" in guessed
    assert '<span class="badge">guess</span>' in guessed

    response = client.post("/api/chat", json={"message": "note 1 my own words"})
    assert response.json() == {"kind": "text", "text": "Reason updated."}
    item = store.get_bookmark(1)
    assert item["reason"] == "my own words"
    assert item["reason_source"] == "user"

    reloaded = client.get("/bookmarks").text
    assert "my own words" in reloaded
    assert "guess" not in reloaded.lower()
