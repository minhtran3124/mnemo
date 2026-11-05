import pytest
from fastapi.testclient import TestClient

import store

FAKE_KEY = "sk-ant-fake-key-for-tests"


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


def seed(**overrides):
    record = {
        "url": "https://www.example.com/a?x=1",
        "url_clean": "https://example.com/a",
        "type": "article",
        "title": "An article",
        "page_status": "ok",
        "summary": "A short summary.",
        "tags": ["testing", "login", "python"],
        "reason": "",
        "reason_source": "guess",
        "folder": None,
        "opened_count": 0,
    }
    record.update(overrides)
    return store.add_bookmark(record, page_text="page body")


def test_page_is_served_and_empty_page_has_no_folder_banner_or_move(client):
    empty = client.get("/bookmarks")

    assert empty.status_code == 200
    assert empty.headers["content-type"].startswith("text/html")
    assert 'class="site-header"' in empty.text
    assert '<p class="empty" id="bm-empty">' in empty.text
    assert 'id="bm-folder"' not in empty.text
    assert 'id="bm-banner"' not in empty.text

    seed()
    text = client.get("/bookmarks").text

    assert 'id="bm-folder"' in text
    assert "Move" not in text
    assert "Needs a look" not in text


def test_row_shows_fields_flags_guess_and_survives_odd_records(client, monkeypatch):
    seed(title="<script>alert(1)</script>", tags=["alpha", "beta", "gamma"])
    text = client.get("/bookmarks").text

    assert "<script>alert(1)</script>" not in text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in text
    assert "article" in text
    assert "www.example.com" in text
    for tag in ("alpha", "beta", "gamma"):
        assert tag in text
    assert store.list_bookmarks()[0]["saved_at"][:10] in text

    store.delete_bookmark(1)
    seed(reason="Looks useful for login work", reason_source="guess")
    guess_text = client.get("/bookmarks").text
    assert "Looks useful for login work" in guess_text
    assert "guess" in guess_text.lower()

    store.delete_bookmark(2)
    seed(reason="Needed for my talk", reason_source="user")
    user_text = client.get("/bookmarks").text
    assert "Needed for my talk" in user_text
    assert "guess" not in user_text.lower()

    odd = {"id": 7, "url": "https://example.com/bare", "type": "podcast", "tags": "abc"}
    monkeypatch.setattr(store, "list_bookmarks", lambda *a, **k: [odd])
    response = client.get("/bookmarks")
    assert response.status_code == 200
    assert 'data-type="other"' in response.text
    assert "https://example.com/bare" in response.text
    assert "<li>a</li>" not in response.text


def test_unreadable_bookmark_shows_badge_banner_and_script_hooks(client):
    seed(page_status="unreadable", summary=None, title="Locked page")
    seed(url="https://example.com/b", url_clean="https://example.com/b")

    text = client.get("/bookmarks").text

    assert "page not read" in text
    assert "Needs a look" in text
    assert 'id="bm-banner"' in text
    assert text.count('data-unreadable="true"') == 1
    assert '<p class="empty" id="bm-empty" hidden>' in text


def test_title_link_carries_the_open_url(client):
    saved = seed()

    text = client.get("/bookmarks").text

    assert f'data-open-url="/api/bookmarks/{saved["id"]}/open"' in text
    assert 'href="https://www.example.com/a?x=1"' in text.replace("&amp;", "&")


def test_delete_button_carries_delete_url_and_confirm_text(client):
    saved = seed(title="Quarterly plan")

    text = client.get("/bookmarks").text

    assert f'data-delete-url="/api/bookmarks/{saved["id"]}"' in text
    confirm = text.split('data-confirm="', 1)[1].split('"', 1)[0]
    assert "Quarterly plan" in confirm


NODE_HARNESS = """
const fs = require("fs");
const mode = process.argv[3];
let handler;
const status = { textContent: "", hidden: true };
const removed = [];
const empty = { hidden: true };
const button = {
  disabled: false,
  textContent: "Delete",
  getAttribute: (n) => (n === "data-confirm" ? "Sure?" : "/x"),
  closest: () => row,
};
const row = { closest: () => null, remove() {} };
global.window = { confirm: () => true };
global.fetch = () => Promise.resolve({ ok: true });
global.document = {
  getElementById: (id) => {
    if (id === "bm-status") return status;
    if (id === "bm-empty") return empty;
    return { remove: () => removed.push(id) };
  },
  querySelector: () => {
    if (mode === "fault") throw new Error("cleanup fault");
    return null;
  },
  addEventListener: (_, fn) => (handler = fn),
};
eval(fs.readFileSync(process.argv[2], "utf8"));
process.on("unhandledRejection", () => {});
handler({ target: { closest: (sel) => (sel.startsWith("button") ? button : null) } });
setTimeout(() => {
  console.log(JSON.stringify({ status: status.textContent, removed, emptyHidden: empty.hidden }));
}, 20);
"""


def run_script_after_delete(tmp_path, mode):
    import json
    import shutil
    import subprocess
    from pathlib import Path

    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    harness = tmp_path / "harness.js"
    harness.write_text(NODE_HARNESS)
    script = Path(__file__).resolve().parent.parent / "web" / "js" / "bookmarks.js"
    result = subprocess.run(
        [node, str(harness), str(script), mode],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_script_clears_folder_after_last_delete_and_hides_false_errors(tmp_path):
    last = run_script_after_delete(tmp_path, "last")
    assert last["removed"] == ["bm-banner", "bm-folder"]
    assert last["emptyHidden"] is False
    assert last["status"] == ""

    fault = run_script_after_delete(tmp_path, "fault")
    assert fault["status"] == ""
