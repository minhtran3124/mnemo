import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mnemo.core import store

FAKE_KEY = "sk-ant-fake-key-for-tests"
COLOUR_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")
WEB = Path(__file__).resolve().parents[2] / "mnemo" / "api" / "web"


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    from mnemo.api import server

    return TestClient(server.app)


# A tiny fake DOM and a stubbed fetch. It loads web/js/chat.js, optionally
# types text into the first Paste box and presses its Save button, then prints
# what the page drew and every fetch it made.
NODE_HARNESS = r"""
const fs = require("fs");
const config = JSON.parse(process.argv[3]);

class Node {
  constructor(tag) {
    this.tag = tag; this.children = []; this.listeners = {}; this.attrs = {};
    this.className = ""; this.own = ""; this.hidden = false;
    this.disabled = false; this.value = ""; this.parent = null;
  }
  set textContent(v) { this.children = []; this.own = String(v); }
  get textContent() { return this.own + this.children.map((c) => c.textContent).join(" "); }
  appendChild(c) { c.parent = this; this.children.push(c); return c; }
  replaceWith(...nodes) {
    const at = this.parent.children.indexOf(this);
    nodes.forEach((n) => (n.parent = this.parent));
    this.parent.children.splice(at, 1, ...nodes);
  }
  setAttribute(k, v) { this.attrs[k] = v; }
  getAttribute(k) { return this.attrs[k]; }
  addEventListener(type, fn) { (this.listeners[type] = this.listeners[type] || []).push(fn); }
  focus() {}
  requestSubmit() {}
  click() { (this.listeners.click || []).forEach((fn) => fn({})); }
  all() { return [this, ...this.children.flatMap((c) => c.all())]; }
}

const ids = {};
for (const id of ["chat-log", "chat-empty", "chat-form", "chat-message", "chat-save", "chat-status"]) {
  ids[id] = new Node(id);
}
global.window = { scrollTo() {} };
global.document = {
  body: { scrollHeight: 0 },
  getElementById: (id) => ids[id],
  createElement: (tag) => new Node(tag),
  createElementNS: (ns, tag) => new Node(tag),
  createTextNode: (t) => { const n = new Node("#text"); n.own = t; return n; },
};

const fetches = [];
global.fetch = (url, opts) => {
  fetches.push({ url, method: opts && opts.method, body: opts && opts.body });
  const answer = url === "/api/chat/history" ? config.history : config.paste;
  return Promise.resolve({
    ok: answer.status < 400,
    status: answer.status,
    json: () => Promise.resolve(answer.body),
  });
};
process.on("unhandledRejection", (e) => { console.error(e); process.exit(1); });

eval(fs.readFileSync(process.argv[2], "utf8"));

const wait = () => new Promise((r) => setTimeout(r, 20));
const log = ids["chat-log"];

(async () => {
  await wait();
  if (config.paste) {
    const area = log.all().find((n) => n.tag === "textarea");
    area.value = config.text;
    const card = log.children[0];
    const save = card.all().find((n) => n.tag === "button" && n.textContent === "Save");
    save.click();
    await wait();
  }
  console.log(JSON.stringify({
    fetches,
    cards: log.children.map((c) => ({
      tag: c.tag,
      text: c.textContent,
      textareas: c.all().filter((n) => n.tag === "textarea").length,
      buttons: c.all().filter((n) => n.tag === "button").map((n) => n.textContent),
    })),
  }));
})();
"""


def run_page(tmp_path, history, paste=None, text=""):
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    harness = tmp_path / "harness.js"
    harness.write_text(NODE_HARNESS)
    config = {"history": {"status": 200, "body": {"messages": history}}}
    if paste is not None:
        config["paste"] = paste
        config["text"] = text
    result = subprocess.run(
        [node, str(harness), str(WEB / "js" / "chat.js"), json.dumps(config)],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def record(**overrides):
    base = {
        "id": 7,
        "url": "https://www.example.com/a",
        "type": "article",
        "title": "An article",
        "page_status": "ok",
        "summary": "A short summary.",
        "tags": ["alpha", "beta", "gamma", "delta"],
        "reason": "Useful for login work",
        "reason_source": "guess",
        "folder": None,
    }
    base.update(overrides)
    return base


def assistant(cards, **extra):
    return [{"role": "assistant", "text": "Saved.", "cards": cards, **extra}]


def unread(**overrides):
    return record(
        id=5, page_status="unreadable", summary=None, title="Hidden page", **overrides
    )


def test_chat_page_is_served_with_message_box_and_shared_header(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    text = response.text
    assert 'class="site-header"' in text
    assert "<!--HEADER-->" not in text
    assert re.search(r"<(textarea|input)[^>]*\bid=", text)
    assert re.search(r"<label[^>]*\bfor=", text)
    assert re.search(r"<button[^>]*>\s*Save\s*</button>", text)
    assert "/static/js/chat.js" in text


def test_card_has_every_field_and_files_have_no_colour_literal(client, tmp_path):
    out = run_page(tmp_path, assistant([record()]))

    text = out["cards"][0]["text"]
    for part in (
        "An article",
        "Article on example.com",
        "alpha, beta, gamma",
        "A short summary.",
        "Why you saved it:",
        "Useful for login work",
        "guess",
        "No. 7",
        "Filed in",
        "Unsorted",
    ):
        assert part in text
    assert "delta" not in text

    for name in ("index.html", "css/chat.css", "js/chat.js"):
        assert not COLOUR_LITERAL.search((WEB / name).read_text()), name


def test_page_not_read_card_has_paste_box_and_move_controls(client, tmp_path):
    out = run_page(tmp_path, assistant([unread()]))

    card = out["cards"][0]
    assert "Page not read" in card["text"]
    assert card["textareas"] == 1
    assert "Paste the text" in card["buttons"]
    assert "Move" in card["buttons"]
    assert "Undo" in card["buttons"]
    assert "A short summary." not in card["text"]


def test_history_loads_on_start_and_handles_deleted_and_failed_entries(tmp_path):
    messages = assistant(
        [{"id": 3, "deleted": True}, record()], failed=["https://nope.example/x"]
    )
    out = run_page(tmp_path, messages)

    assert out["fetches"][0]["url"] == "/api/chat/history"
    texts = [c["text"] for c in out["cards"]]
    assert texts[0] == "Bookmark 3 was deleted."
    assert "An article" in texts[1]
    failed = out["cards"][2]
    assert "I could not save this link." in failed["text"]
    assert failed["textareas"] == 0
    # A stored message with no failed[] draws nothing extra.
    plain = run_page(tmp_path, assistant([record()]))
    assert len(plain["cards"]) == 2
    assert plain["cards"][1]["text"] == "Saved."


def test_paste_posts_to_the_bookmark_route_maps_error_codes_and_replaces_the_card(
    tmp_path,
):
    errors = [
        (
            400,
            "text_too_short",
            "That text is too short to read. Paste more of the page.",
        ),
        (
            502,
            "summary_failed",
            "I could not make a summary from that text. The bookmark is unchanged.",
        ),
        (409, "already_read", "That bookmark was already read."),
        (500, "boom", "Something went wrong. Try again."),
    ]
    for status, code, expected in errors:
        body = {"error": {"code": code, "message": "server wording"}}
        out = run_page(
            tmp_path,
            assistant([unread()]),
            paste={"status": status, "body": body},
            text="some pasted text",
        )

        call = out["fetches"][-1]
        assert call["url"] == "/api/bookmarks/5/paste"
        assert call["method"] == "POST"
        assert json.loads(call["body"]) == {"text": "some pasted text"}
        card = out["cards"][0]
        assert expected in card["text"]
        assert "server wording" not in card["text"]
        assert card["textareas"] == 1

    updated = record(id=5, title="Now read", summary="Fresh summary.")
    out = run_page(
        tmp_path,
        assistant([unread()]),
        paste={"status": 200, "body": updated},
        text="the page text",
    )
    card = out["cards"][0]
    assert "Now read" in card["text"]
    assert "Fresh summary." in card["text"]
    assert card["textareas"] == 0
    assert "Page not read" not in card["text"]
