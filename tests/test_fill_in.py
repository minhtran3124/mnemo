import pytest
from fastapi.testclient import TestClient

import save
import store

PASTE = "  some   pasted\ntext " * 10  # well over the pasted-text floor


def good(**overrides):
    fields = {
        "title": "A real title",
        "type": "article",
        "summary": "A short summary of the pasted text.",
        "tags": ["Python", "testing", "web"],
        "reason": "Looks useful.",
    }
    fields.update(overrides)
    return save.SaveOutput(**fields)


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake-key-for-tests")
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


@pytest.fixture
def parse_calls(monkeypatch):
    state = {"replies": [good()], "calls": []}

    def fake(messages, output_format, system=None):
        state["calls"].append(messages)
        return state["replies"].pop(0)

    monkeypatch.setattr(save.client, "parse", fake)
    return state


def seed(**overrides):
    record = {
        "url": "https://example.com/a",
        "url_clean": "https://example.com/a",
        "type": "article",
        "title": "example.com",
        "page_status": "unreadable",
        "summary": None,
        "tags": [],
        "reason": "for my talk",
        "reason_source": "user",
        "folder": None,
        "opened_count": 3,
    }
    record.update(overrides)
    return store.add_bookmark(record, page_text=None)


def test_fill_in_updates_same_bookmark(client, parse_calls):
    before = seed()
    res = client.post(f"/api/bookmarks/{before['id']}/paste", json={"text": PASTE})
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == before["id"]
    assert body["saved_at"] == before["saved_at"]
    assert body["opened_count"] == 3
    assert body["reason"] == "for my talk"
    assert body["reason_source"] == "user"
    assert body["page_status"] == "ok"
    assert body["summary"]
    assert store.get_bookmark(before["id"]) == body
    assert len(store.list_bookmarks()) == 1


def test_text_under_floor_is_400_and_changes_nothing(client, parse_calls):
    before = seed()
    res = client.post(f"/api/bookmarks/{before['id']}/paste", json={"text": "short"})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "text_too_short"
    assert store.get_bookmark(before["id"]) == before
    assert store.read_page(before["id"]) is None
    assert parse_calls["calls"] == []


def test_unknown_id_is_404(client, parse_calls):
    res = client.post("/api/bookmarks/99/paste", json={"text": PASTE})
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "bookmark_not_found"


def test_readable_bookmark_is_409(client, parse_calls):
    ok = seed(page_status="ok", summary="Already read.", tags=["a", "b", "c"])
    res = client.post(f"/api/bookmarks/{ok['id']}/paste", json={"text": PASTE})
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "already_read"
    assert store.get_bookmark(ok["id"]) == ok
    assert parse_calls["calls"] == []


def test_invalid_output_twice_is_502_and_changes_nothing(client, parse_calls):
    before = seed()
    parse_calls["replies"] = [good(tags=["one"]), good(tags=["one"])]
    res = client.post(f"/api/bookmarks/{before['id']}/paste", json={"text": PASTE})
    assert res.status_code == 502
    assert res.json()["error"]["code"] == "summary_failed"
    assert store.get_bookmark(before["id"]) == before
    assert store.read_page(before["id"]) is None


def test_stored_page_equals_text_sent_to_claude(client, parse_calls):
    before = seed()
    client.post(f"/api/bookmarks/{before['id']}/paste", json={"text": PASTE})
    sent = parse_calls["calls"][0][0]["content"]
    stored = store.read_page(before["id"])
    assert stored == " ".join(PASTE.split())
    assert f"<page>\n{stored}\n</page>" == sent
