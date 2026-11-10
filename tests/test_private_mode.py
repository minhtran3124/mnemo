"""Private mode: `private <link>` saves link only with no API call (F-19, D-017)."""

import pytest
from fastapi.testclient import TestClient

import save
import store

FAKE_KEY = "sk-ant-fake-key-for-tests"


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


def record(**overrides):
    fields = {
        "url": "https://example.com/a",
        "url_clean": "https://example.com/a",
        "type": "article",
        "title": "An article",
        "page_status": "ok",
        "summary": "A short summary.",
        "tags": ["testing", "login", "python"],
        "reason": "",
        "reason_source": "guess",
        "folder": None,
        "opened_count": 0,
    }
    fields.update(overrides)
    return fields


def test_private_chat_saves_one_link_only_bookmark(api, monkeypatch):
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: pytest.fail("private save fetched a page")
    )

    response = api.post("/api/chat", json={"message": "private https://example.com/a"})

    assert response.status_code == 200
    cards = response.json()["cards"]
    assert len(cards) == 1
    assert cards[0]["private"] is True
    assert cards[0]["page_status"] == "unreadable"
    assert cards[0]["summary"] is None
    assert cards[0]["url"] == "https://example.com/a"


def test_private_save_succeeds_when_the_claude_client_raises(api, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("the Claude client must not be called")

    monkeypatch.setattr(save.client, "parse", boom)

    response = api.post("/api/chat", json={"message": "private https://example.com/a"})

    assert response.status_code == 200
    assert response.json()["cards"][0]["private"] is True
    assert len(store.list_bookmarks()) == 1


def test_private_save_writes_no_api_call_event(api, tmp_path):
    api.post("/api/chat", json={"message": "private https://example.com/a"})

    log = tmp_path / "log.jsonl"
    lines = store._read_lines(log) if log.exists() else []
    assert not [line for line in lines if line.get("event") in {"api_call", "claude"}]
    assert not (tmp_path / "pages" / "1.txt").exists()


def test_a_normal_link_is_not_private(api, monkeypatch):
    def fake_save(url, pasted_text=None, private=False):
        return store.add_bookmark(record(private=private), page_text=None)

    monkeypatch.setattr(save, "save", fake_save)

    response = api.post("/api/chat", json={"message": "https://example.com/a"})

    assert response.json()["cards"][0]["private"] is False


def test_private_without_a_link_is_a_question(api):
    response = api.post("/api/chat", json={"message": "private"})

    assert response.json() == {
        "kind": "text",
        "text": "I can only save links for now. Asking comes later.",
    }
    assert store.list_bookmarks() == []


def test_store_requires_a_boolean_private_field():
    saved = store.add_bookmark(record(), page_text=None)
    assert saved["private"] is False

    with pytest.raises(store.InvalidRecord, match="private"):
        store.add_bookmark(record(private="yes"), page_text=None)
