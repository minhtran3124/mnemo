import pytest
from fastapi.testclient import TestClient

import store


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake-key-for-tests")
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


def test_page_has_switcher_with_cards_and_ledger_labels(client):
    html = client.get("/bookmarks").text

    assert ">Cards</button>" in html
    assert ">Ledger</button>" in html
    assert "/static/js/view-switcher.js" in html


def test_each_label_sets_a_different_view_class(client):
    script = client.get("/static/js/view-switcher.js").text

    assert "view-cards" in script
    assert "view-ledger" in script


def test_stored_choice_is_read_on_load_with_ledger_default(client):
    script = client.get("/static/js/view-switcher.js").text

    assert "localStorage.getItem(STORAGE_KEY)" in script
    assert 'DEFAULT_VIEW = "ledger"' in script
