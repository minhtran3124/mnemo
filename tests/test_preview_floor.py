import pytest

import save
import store

TEXT = "x" * 100  # over the GitHub floor, under the HTML floor


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)

    def fake(messages, output_format, system=None):
        return save.SaveOutput(
            title="A page",
            type="article",
            summary="A short summary of the page.",
            tags=["Python", "testing", "web"],
            reason="Looks useful.",
        )

    monkeypatch.setattr(save.client, "parse", fake)


def test_repo_url_uses_github_floor():
    record = save.preview("https://github.com/octo/hello", TEXT)
    assert record["page_status"] == "ok"


def test_github_non_repo_url_uses_html_floor():
    record = save.preview("https://github.com/blog/post", TEXT)
    assert record["page_status"] == "unreadable"
    assert record["summary"] is None


def test_other_host_uses_html_floor():
    record = save.preview("https://example.com/a", TEXT)
    assert record["page_status"] == "unreadable"
    assert record["summary"] is None
