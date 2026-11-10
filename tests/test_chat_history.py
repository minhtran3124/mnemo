import pytest
from fastapi.testclient import TestClient

import ask
import fetcher
import save
import store

FAKE_KEY = "sk-ant-fake-key-for-tests"
LONG = "word " * 100


def good():
    return save.SaveOutput(
        title="A post",
        type="article",
        summary="A short summary of the post.",
        tags=["python", "testing", "web"],
        reason="Looks useful.",
    )


@pytest.fixture
def data_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchOk(text=LONG, source="web")
    )
    monkeypatch.setattr(
        save.client, "parse", lambda messages, output_format, system=None: good()
    )
    monkeypatch.setattr(
        ask, "run_ask", lambda question: ask.AskResult(text="nothing found")
    )
    return tmp_path


def make_api():
    import server

    return TestClient(server.app)


def test_exchange_appends_both_sides(data_dir):
    api = make_api()
    api.post("/api/chat", json={"message": "hello there"})

    lines = store.list_chat()
    assert [(m["role"], m["text"]) for m in lines] == [
        ("user", "hello there"),
        ("app", "nothing found"),
    ]
    assert api.post("/api/chat", json={"message": "  "}).status_code == 400
    assert len(store.list_chat()) == 2


def test_history_returns_messages_in_order(data_dir):
    api = make_api()
    api.post("/api/chat", json={"message": "first"})
    api.post("/api/chat", json={"message": "second"})

    body = api.get("/api/chat/history").json()
    assert [m["id"] for m in body["messages"]] == [1, 2, 3, 4]
    assert [m["text"] for m in body["messages"] if m["role"] == "user"] == [
        "first",
        "second",
    ]
    assert len(api.get("/api/chat/history?limit=3").json()["messages"]) == 3
    assert api.get("/api/chat/history?limit=0").status_code == 400


def test_card_reply_is_returned_with_card_fields(data_dir):
    api = make_api()
    card = api.post("/api/chat", json={"message": "save https://example.com/a"}).json()[
        "cards"
    ][0]

    reply = api.get("/api/chat/history").json()["messages"][1]
    assert reply["bookmark_ids"] == [card["id"]]
    assert reply["cards"][0]["title"] == "A post"
    assert reply["cards"][0]["summary"] == "A short summary of the post."

    api.delete(f"/api/bookmarks/{card['id']}")
    reply = api.get("/api/chat/history").json()["messages"][1]
    assert reply["cards"] == [{"id": card["id"], "deleted": True}]


def test_new_app_instance_returns_the_same_history(data_dir):
    first = make_api()
    first.post("/api/chat", json={"message": "save https://example.com/a"})
    before = first.get("/api/chat/history").json()

    after = make_api().get("/api/chat/history").json()
    assert after == before
    assert len(after["messages"]) == 2

    import server

    assert server._cards_reply_text(0, 2) == "I could not save any of the 2 links."
    assert server._cards_reply_text(0, 1) == "I could not save it."
    assert server._cards_reply_text(1, 0) == "Saved 1 bookmark."
    assert server._cards_reply_text(2, 1) == "Saved 2 bookmarks. 1 could not be saved."


def test_note_exchange_is_recorded_in_history(data_dir):
    api = make_api()
    api.post("/api/chat", json={"message": "note 3"})
    api.post("/api/chat", json={"message": "note 999 text"})
    texts = [m["text"] for m in api.get("/api/chat/history").json()["messages"]]
    assert texts == [
        "note 3",
        "What should the reason say? Write note <id> <text>.",
        "note 999 text",
        "I do not have a bookmark with that number.",
    ]
