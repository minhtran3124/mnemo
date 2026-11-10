"""Move and Undo on the chat card and on every bookmark row (FO-05, BP-05)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import config
import store

FAKE_KEY = "sk-ant-fake-key-for-tests"
ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


def seed(folder: str | None = None, prev_folder: str | None = None) -> dict:
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
            "prev_folder": prev_folder,
            "opened_count": 0,
        },
        page_text="page body",
    )


def test_filed_card_source_shows_filed_in_move_and_undo():
    script = (ROOT / "web" / "js" / "chat.js").read_text(encoding="utf-8")

    assert '"Filed in: "' in script
    assert '"Move"' in script
    assert '"Undo"' in script
    assert '"/api/bookmarks/" + record.id' in script
    assert '"/undo"' in script
    assert "STARTER_FOLDERS" in script
    assert "UNSORTED" in script


def test_bookmark_row_move_control_lists_all_folders(api):
    seed(folder="Work", prev_folder=config.UNSORTED)

    text = api.get("/bookmarks").text

    assert "Filed in: <strong>Work</strong>" in text
    assert 'class="bm-move-select"' in text
    for name in (*config.STARTER_FOLDERS, config.UNSORTED):
        assert f'<option value="{name}"' in text
    assert 'value="Work" selected' in text
    assert 'data-move-url="/api/bookmarks/1"' in text
    assert 'data-undo-url="/api/bookmarks/1/undo"' in text


def test_card_move_then_undo_returns_the_first_folder(api):
    seed(folder="Work")

    moved = api.patch("/api/bookmarks/1", json={"folder": "Learning"}).json()
    undone = api.post("/api/bookmarks/1/undo").json()

    assert moved["folder"] == "Learning"
    assert moved["prev_folder"] == "Work"
    assert undone["folder"] == "Work"
    assert undone["prev_folder"] is None


def test_row_move_then_undo_returns_the_first_folder(api):
    seed(folder="Reference")
    text = api.get("/bookmarks").text
    move_url = text.split('data-move-url="', 1)[1].split('"', 1)[0]

    moved = api.patch(move_url, json={"folder": "Ideas"}).json()
    assert moved["folder"] == "Ideas"

    after = api.get("/bookmarks").text
    undo_url = after.split('data-undo-url="', 1)[1].split('"', 1)[0]
    undone = api.post(undo_url).json()

    assert undone["folder"] == "Reference"


def test_a_failed_move_shows_the_api_message_and_changes_nothing(api):
    seed(folder="Work")
    script = (ROOT / "web" / "js" / "bookmarks.js").read_text(encoding="utf-8")

    response = api.patch("/api/bookmarks/1", json={"folder": "Archive"})

    assert response.status_code == 400
    assert response.json()["error"]["message"] == "Folder does not exist."
    assert store.get_bookmark(1)["folder"] == "Work"
    assert "showError(message)" in script
    assert "body.error.message" in script
