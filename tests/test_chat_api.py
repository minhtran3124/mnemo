import pytest
from fastapi.testclient import TestClient

import fetcher
import save
import store

FAKE_KEY = "sk-ant-fake-key-for-tests"
LINKS_ONLY = "I can only save links for now. Asking comes later."
LONG = "word " * 100


def good(**overrides):
    fields = {
        "title": "A post",
        "type": "article",
        "summary": "A short summary of the post.",
        "tags": ["python", "testing", "web"],
        "reason": "Looks useful.",
    }
    fields.update(overrides)
    return save.SaveOutput(**fields)


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


@pytest.fixture
def fetch_calls(monkeypatch):
    calls = []

    def fake(url):
        calls.append(url)
        return fetcher.FetchOk(text=LONG, source="web")

    monkeypatch.setattr(save.fetcher, "fetch", fake)
    return calls


@pytest.fixture
def parse_calls(monkeypatch):
    calls = []

    def fake(messages, output_format, system=None):
        calls.append(messages)
        return good()

    monkeypatch.setattr(save.client, "parse", fake)
    return calls


def test_link_message_returns_a_card(api, fetch_calls, parse_calls):
    response = api.post("/api/chat", json={"message": "save https://example.com/a"})

    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == "cards"
    card = body["cards"][0]
    assert isinstance(card["id"], int)
    assert card["title"] == "A post"
    assert card["type"] == "article"
    assert card["tags"] == ["python", "testing", "web"]
    assert card["summary"] == "A short summary of the post."
    assert fetch_calls == ["https://example.com/a"]


def test_message_without_a_link_gets_the_links_only_text(api):
    response = api.post("/api/chat", json={"message": "what is a bookmark?"})

    assert response.status_code == 200
    assert response.json() == {"kind": "text", "text": LINKS_ONLY}


def test_message_without_a_link_calls_neither_claude_nor_the_fetcher(
    api, fetch_calls, parse_calls
):
    api.post("/api/chat", json={"message": "hello there"})

    assert parse_calls == []
    assert fetch_calls == []
    assert store.list_bookmarks() == []


def test_blank_message_is_a_400_empty_message(api):
    for message in ("", "   \n\t "):
        response = api.post("/api/chat", json={"message": message})

        assert response.status_code == 400
        assert response.json()["error"]["code"] == "empty_message"


def test_pasted_text_is_summarised_without_fetching(api, fetch_calls, parse_calls):
    pasted = "pasted words " * 10
    response = api.post(
        "/api/chat",
        json={"message": "https://example.com/slack", "pasted_text": pasted},
    )

    assert response.status_code == 200
    assert response.json()["cards"][0]["page_status"] == "ok"
    assert fetch_calls == []
    assert len(parse_calls) == 1
    assert "pasted words" in parse_calls[0][0]["content"]


def test_unreadable_page_returns_a_link_only_card(api, monkeypatch, parse_calls):
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchFail("timed out")
    )

    response = api.post("/api/chat", json={"message": "https://example.com/gone"})

    card = response.json()["cards"][0]
    assert card["page_status"] == "unreadable"
    assert card["summary"] is None
    assert parse_calls == []


def test_links_save_in_order_and_duplicates_once(api, fetch_calls, parse_calls):
    response = api.post(
        "/api/chat",
        json={
            "message": "https://example.com/a https://example.com/b "
            "https://example.com/a?utm_source=x"
        },
    )

    body = response.json()
    assert [c["url"] for c in body["cards"]] == [
        "https://example.com/a",
        "https://example.com/b",
    ]
    assert "failed" not in body
    assert len(store.list_bookmarks()) == 2


def test_later_link_failure_keeps_the_saved_cards(api, fetch_calls, monkeypatch):
    real = save.save

    def fake(url, pasted_text=None):
        if "bad" in url:
            raise store.StoreError("disk full")
        return real(url, pasted_text=pasted_text)

    monkeypatch.setattr(save.client, "parse", lambda *a, **k: good())
    monkeypatch.setattr(save, "save", fake)

    response = api.post(
        "/api/chat",
        json={"message": "https://example.com/a https://example.com/bad"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["cards"]) == 1
    assert body["failed"] == ["https://example.com/bad"]
    assert len(store.list_bookmarks()) == 1


def test_later_unexpected_error_keeps_the_saved_cards(api, fetch_calls, monkeypatch):
    real = save.save

    def fake(url, pasted_text=None):
        if "bad" in url:
            raise RuntimeError("boom")
        return real(url, pasted_text=pasted_text)

    monkeypatch.setattr(save.client, "parse", lambda *a, **k: good())
    monkeypatch.setattr(save, "save", fake)

    response = api.post(
        "/api/chat",
        json={"message": "https://example.com/a https://example.com/bad"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["cards"]) == 1
    assert body["failed"] == ["https://example.com/bad"]
    assert len(store.list_bookmarks()) == 1
