import pytest
from fastapi.testclient import TestClient

from mnemo.core import store

FAKE_KEY = "sk-ant-fake-key-for-tests"


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    from mnemo.api import server

    return TestClient(server.app)


def seed(n: int = 3) -> None:
    for i in range(n):
        store.add_bookmark(
            {
                "url": f"https://example.com/{i}",
                "url_clean": f"https://example.com/{i}",
                "type": "article",
                "title": f"Article {i}",
                "page_status": "ok",
                "summary": "A short summary.",
                "tags": ["testing", "login", "python"],
                "reason": "Looks useful.",
                "reason_source": "guess",
                "folder": None,
                "opened_count": 0,
            },
            page_text="page body",
        )


def test_patch_sets_reason(api):
    seed()
    response = api.patch("/api/bookmarks/3", json={"reason": "for login tests"})
    assert response.status_code == 200
    assert response.json()["reason"] == "for login tests"
    assert store.get_bookmark(3)["reason"] == "for login tests"


def test_patch_sets_reason_source_to_user(api):
    seed()
    response = api.patch("/api/bookmarks/3", json={"reason": "mine"})
    assert response.json()["reason_source"] == "user"
    assert store.get_bookmark(3)["reason_source"] == "user"


def test_patch_unknown_id_is_404(api):
    seed()
    response = api.patch("/api/bookmarks/999", json={"reason": "x"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "bookmark_not_found"


def test_note_command_changes_the_reason(api):
    seed()
    response = api.post("/api/chat", json={"message": "note 3 some text"})
    assert response.json() == {"kind": "text", "text": "Reason updated."}
    item = store.get_bookmark(3)
    assert item["reason"] == "some text"
    assert item["reason_source"] == "user"


def test_note_unknown_id_reply(api):
    seed()
    response = api.post("/api/chat", json={"message": "note 999 text"})
    assert response.json() == {
        "kind": "text",
        "text": "I do not have a bookmark with that number.",
    }


def test_note_without_text_reply(api):
    seed()
    response = api.post("/api/chat", json={"message": "note 3"})
    assert response.json() == {
        "kind": "text",
        "text": "What should the reason say? Write note <id> <text>.",
    }
    assert store.get_bookmark(3)["reason"] == "Looks useful."
