"""A question routes to ask and returns up to 3 bookmarks (ticket #125)."""

import pytest
from fastapi.testclient import TestClient

import ask
import save
import store

FAKE_KEY = "sk-ant-fake-key-for-tests"


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app, raise_server_exceptions=False)


def seed(reason: str = "", reason_source: str = "guess") -> dict:
    return store.add_bookmark(
        {
            "url": "https://example.com/a",
            "url_clean": "https://example.com/a",
            "type": "article",
            "title": "An article",
            "page_status": "ok",
            "summary": "A short summary.",
            "tags": ["testing", "login", "python"],
            "reason": reason,
            "reason_source": reason_source,
            "folder": None,
            "opened_count": 0,
        },
        page_text="page body",
    )


def asking(monkeypatch, text: str):
    monkeypatch.setattr(ask, "run_ask", lambda question: ask.AskResult(text=text))


def test_a_link_message_never_reaches_ask(api, monkeypatch):
    def fake_save(url, pasted_text=None, private=False, prompt_version=None):
        return seed()

    monkeypatch.setattr(save, "save", fake_save)

    def must_not_ask(question):
        pytest.fail("a link must not reach ask")

    monkeypatch.setattr(ask, "run_ask", must_not_ask)

    response = api.post("/api/chat", json={"message": "https://example.com/a"})

    assert response.status_code == 200
    assert response.json()["kind"] == "cards"


def test_four_picked_bookmarks_return_only_three(api, monkeypatch):
    for _ in range(4):
        seed()
    asking(monkeypatch, "Found #1, #2, #3 and #4.")

    response = api.post("/api/chat", json={"message": "which ones fit?"})

    answer = response.json()
    assert answer["kind"] == "answer"
    assert [item["id"] for item in answer["bookmarks"]] == [1, 2, 3]
    assert len(answer["bookmarks"]) == 3


def test_no_match_returns_nothing_found(api, monkeypatch):
    asking(monkeypatch, "nothing found")

    response = api.post("/api/chat", json={"message": "what about quantum cooking?"})

    assert response.json() == {
        "kind": "answer",
        "text": "nothing found",
        "bookmarks": [],
    }


def test_a_guessed_reason_is_marked(api, monkeypatch):
    bookmark = seed(reason="Looks useful for login work")
    asking(monkeypatch, f"Use #{bookmark['id']}.")

    answer = api.post("/api/chat", json={"message": "login?"}).json()

    item = answer["bookmarks"][0]
    assert item["id"] == bookmark["id"]
    assert item["reason"] == "Looks useful for login work"
    assert item["reason_source"] == "guess"


def test_question_and_answer_are_in_history(api, monkeypatch):
    bookmark = seed()
    asking(monkeypatch, f"Use #{bookmark['id']}.")

    api.post("/api/chat", json={"message": "which bookmark fits?"})

    messages = api.get("/api/chat/history").json()["messages"]
    assert [message["role"] for message in messages] == ["user", "app"]
    assert messages[0]["text"] == "which bookmark fits?"
    assert messages[1]["text"] == f"Use #{bookmark['id']}."
    assert messages[1]["bookmark_ids"] == [bookmark["id"]]


def test_a_claude_error_returns_the_server_error_format(api, monkeypatch):
    def boom(question):
        raise RuntimeError("boom")

    monkeypatch.setattr(ask, "run_ask", boom)

    response = api.post("/api/chat", json={"message": "a question"})

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "server_error"
