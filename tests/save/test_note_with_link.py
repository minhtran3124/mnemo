import pytest
from fastapi.testclient import TestClient

from mnemo import fetcher
from mnemo.core import store
from mnemo.save import pipeline as save

FAKE_KEY = "sk-ant-fake-key-for-tests"
LONG = "word " * 100


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchOk(text=LONG, source="web")
    )
    monkeypatch.setattr(
        save.client,
        "parse",
        lambda messages, output_format, system=None: save.SaveOutput(
            title="A post",
            type="article",
            summary="A short summary of the post.",
            tags=["python", "testing", "web"],
            reason="Looks useful.",
        ),
    )
    from mnemo.api import server

    return TestClient(server.app)


def seed(n: int = 3) -> None:
    for i in range(n):
        store.add_bookmark(
            {
                "url": f"https://example.com/seed{i}",
                "url_clean": f"https://example.com/seed{i}",
                "type": "article",
                "title": f"Article {i}",
                "page_status": "ok",
                "summary": "A short summary.",
                "tags": ["testing", "login", "python"],
                "reason": "Original reason.",
                "reason_source": "guess",
                "folder": None,
                "opened_count": 0,
            },
            page_text="page body",
        )


def reason_of(bookmark_id: int) -> str:
    return next(b for b in store.list_bookmarks() if b["id"] == bookmark_id)["reason"]


def test_note_with_a_link_saves_the_link(api):
    seed()

    response = api.post(
        "/api/chat", json={"message": "note 3 see https://example.com/a"}
    )

    body = response.json()
    assert body["kind"] == "cards"
    assert body["cards"][0]["id"] == 4
    assert reason_of(3) == "Original reason."


def test_note_without_a_link_is_still_a_note(api):
    seed()

    response = api.post("/api/chat", json={"message": "note 3 plain text"})

    assert response.json() == {"kind": "text", "text": "Reason updated."}
    assert reason_of(3) == "plain text"
