import json
import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import fetcher
import save
import store
from tests.test_chat_page import NODE_HARNESS, WEB

FAKE_KEY = "sk-ant-fake-key-for-tests"
LONG = "word " * 100
FAILED = ["https://example.com/bad"]


def good():
    return save.SaveOutput(
        title="A post",
        type="article",
        summary="A short summary of the post.",
        tags=["python", "testing", "web"],
        reason="Looks useful.",
    )


@pytest.fixture
def api(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchOk(text=LONG, source="web")
    )
    monkeypatch.setattr(save.client, "parse", lambda *a, **k: good())
    real = save.save

    def fake(url, pasted_text=None):
        if "bad" in url:
            raise store.StoreError("disk full")
        return real(url, pasted_text=pasted_text)

    monkeypatch.setattr(save, "save", fake)
    import server

    return TestClient(server.app)


def send_partial_failure(api):
    return api.post(
        "/api/chat",
        json={"message": "https://example.com/a https://example.com/bad"},
    )


def test_recorded_app_message_holds_the_failed_links(api):
    send_partial_failure(api)

    app_message = store.list_chat(10)[-1]
    assert app_message["role"] == "app"
    assert app_message["failed"] == FAILED


def test_history_returns_the_failed_links_on_that_message(api):
    send_partial_failure(api)

    messages = api.get("/api/chat/history").json()["messages"]

    assert messages[-1]["role"] == "app"
    assert messages[-1]["failed"] == FAILED


def test_page_draws_failed_links_from_history(tmp_path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    harness = tmp_path / "harness.js"
    harness.write_text(NODE_HARNESS)
    history = [
        {
            "role": "app",
            "text": "Saved 1 bookmark. 1 could not be saved.",
            "cards": [],
            "failed": FAILED,
        }
    ]
    config = {"history": {"status": 200, "body": {"messages": history}}}
    result = subprocess.run(
        [node, str(harness), str(Path(WEB) / "js" / "chat.js"), json.dumps(config)],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout.strip().splitlines()[-1])

    texts = " ".join(c["text"] for c in out["cards"])
    assert "I could not save this link." in texts
    assert FAILED[0] in texts
