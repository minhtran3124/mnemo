import re

import pytest
from fastapi.testclient import TestClient

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
