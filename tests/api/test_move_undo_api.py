"""Move (PATCH folder) and Undo (POST undo) on the bookmark API."""

import pytest
from fastapi.testclient import TestClient

from mnemo.core import config, store

FAKE_KEY = "sk-ant-fake-key-for-tests"


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    from mnemo.api import server

    return TestClient(server.app)


def seed(folder: str | None = None) -> dict:
    return store.add_bookmark(
        {
            "url": "https://example.com/a",
            "url_clean": "https://example.com/a",
            "type": "article",
            "title": "An article",
            "page_status": "ok",
            "summary": "A short summary.",
            "tags": ["testing", "login", "python"],
            "reason": "",
            "reason_source": "guess",
            "folder": folder,
            "opened_count": 0,
        },
        page_text="page body",
    )


def test_move_to_a_starter_folder_keeps_the_old_folder(api):
    seed(folder="Work")

    response = api.patch("/api/bookmarks/1", json={"folder": "Learning"})

    assert response.status_code == 200
    body = response.json()
    assert body["folder"] == "Learning"
    assert body["prev_folder"] == "Work"


def test_move_from_unsorted_keeps_unsorted_for_undo(api):
    seed()

    body = api.patch("/api/bookmarks/1", json={"folder": "Ideas"}).json()

    assert body["folder"] == "Ideas"
    assert body["prev_folder"] == config.UNSORTED


def test_move_to_an_unknown_folder_is_400_and_changes_nothing(api):
    seed(folder="Work")

    response = api.patch("/api/bookmarks/1", json={"folder": "Archive"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "folder_not_found"
    assert store.get_bookmark(1)["folder"] == "Work"
    assert store.get_bookmark(1)["prev_folder"] is None


def test_undo_restores_the_previous_folder(api):
    seed(folder="Work")
    api.patch("/api/bookmarks/1", json={"folder": "Learning"})

    response = api.post("/api/bookmarks/1/undo")

    assert response.status_code == 200
    assert response.json()["folder"] == "Work"
    assert response.json()["prev_folder"] is None


def test_a_second_undo_is_409(api):
    seed(folder="Work")
    api.patch("/api/bookmarks/1", json={"folder": "Learning"})

    assert api.post("/api/bookmarks/1/undo").status_code == 200
    response = api.post("/api/bookmarks/1/undo")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "nothing_to_undo"


def test_undo_on_a_bookmark_that_never_moved_is_409(api):
    seed()

    response = api.post("/api/bookmarks/1/undo")

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "nothing_to_undo"


def test_unknown_id_is_404_for_both_routes(api):
    move = api.patch("/api/bookmarks/99", json={"folder": "Work"})
    undo = api.post("/api/bookmarks/99/undo")

    assert move.status_code == 404
    assert move.json()["error"]["code"] == "bookmark_not_found"
    assert undo.status_code == 404
    assert undo.json()["error"]["code"] == "bookmark_not_found"
