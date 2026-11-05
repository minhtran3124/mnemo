import re

import pytest
from fastapi.testclient import TestClient

import fetcher
import save
import store

FAKE_KEY = "sk-ant-fake-key-for-tests"
COLOUR_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


def script(client):
    response = client.get("/static/js/chat.js")
    assert response.status_code == 200
    return response.text


def test_chat_page_is_served_with_header_message_box_and_save_button(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    text = response.text
    assert 'class="site-header"' in text
    assert "<!--HEADER-->" not in text
    assert re.search(r"<(textarea|input)[^>]*\bid=", text)
    assert re.search(r"<label[^>]*\bfor=", text)
    assert re.search(r"<button[^>]*>\s*Save\s*</button>", text)
    assert "aria-live" in text
    assert "/static/css/chat.css" in text
    assert "/static/js/chat.js" in text


def test_card_markup_has_every_field_and_no_colour_literal(client):
    js = script(client)

    for hook in ("title", "type", "tags", "summary", "reason", "id"):
        assert f"record.{hook}" in js
    assert "reason_source" in js
    assert "Why you saved it:" in js
    assert "Filed in" in js
    assert "Unsorted" in js
    assert "No. " in js

    css = client.get("/static/css/chat.css").text
    page = client.get("/").text
    for name, source in (("chat.js", js), ("chat.css", css), ("index", page)):
        assert not COLOUR_LITERAL.search(source), name


def test_page_not_read_card_has_paste_box_and_sends_pasted_text(client):
    js = script(client)

    assert "Page not read" in js
    assert "Paste the text" in js
    assert "<textarea" in js or 'createElement("textarea")' in js
    assert "pasted_text" in js
    assert "/api/chat" in js
    assert "page_status" in js
    assert "failed" in js


def test_paste_that_is_still_unreadable_keeps_the_card_and_explains(client):
    js = script(client)

    assert "too short to make an entry" in js
    assert 'first.page_status !== "ok"' in js


def test_no_move_or_undo_buttons(client):
    sources = [
        client.get("/").text,
        script(client),
        client.get("/static/css/chat.css").text,
    ]

    for source in sources:
        assert not re.search(r"\b(move|undo)\b", source, re.IGNORECASE)


def test_history_is_loaded_on_start_and_deleted_entries_are_handled(client):
    js = script(client)

    assert "/api/chat/history" in js
    assert "deleted" in js
    assert "was deleted" in js


def test_sending_waits_until_the_history_is_drawn(client):
    js = script(client)

    assert "historyPending" in js
    assert "busy || historyPending" in js
    assert ".then(endHistory)" in js


def _fake_save_calls(monkeypatch):
    monkeypatch.setattr(save.fetcher, "fetch", lambda u: fetcher.FetchFail("blocked"))
    out = save.SaveOutput(
        title="A post",
        type="article",
        summary="A short summary of the post.",
        tags=["python", "testing", "web"],
        reason="Looks useful.",
    )
    monkeypatch.setattr(save.client, "parse", lambda *a, **k: out)


def test_pasted_text_for_a_link_only_entry_replaces_it(client, monkeypatch):
    _fake_save_calls(monkeypatch)
    url = "https://example.com/slack"
    first = client.post("/api/chat", json={"message": url}).json()["cards"][0]
    assert first["page_status"] == "unreadable"

    pasted = "pasted words " * 10
    reply = client.post("/api/chat", json={"message": url, "pasted_text": pasted})

    card = reply.json()["cards"][0]
    assert card["page_status"] == "ok"
    assert [b["id"] for b in client.get("/api/bookmarks").json()] == [card["id"]]


def test_too_short_paste_for_a_link_only_entry_adds_no_second_record(
    client, monkeypatch
):
    _fake_save_calls(monkeypatch)
    url = "https://example.com/slack"
    first = client.post("/api/chat", json={"message": url}).json()["cards"][0]

    reply = client.post("/api/chat", json={"message": url, "pasted_text": "x"})

    assert reply.json()["cards"][0]["id"] == first["id"]
    assert len(client.get("/api/bookmarks").json()) == 1


def test_chat_page_links_to_the_saved_bookmarks_list(client):
    text = client.get("/").text

    assert re.search(r'<a[^>]*href="/bookmarks"', text)
