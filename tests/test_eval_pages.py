"""Tests for the golden page snapshots in evals/golden/."""

import json
from pathlib import Path
from urllib.parse import urlsplit

import config
import save
from evals import save_pages
from fetcher import FetchFail, FetchOk

EVALS_DIR = Path(__file__).resolve().parent.parent / "evals"
PAGES = json.loads((EVALS_DIR / "pages.json").read_text(encoding="utf-8"))
GOLDEN = EVALS_DIR / "golden"


def test_writes_normalised_text(tmp_path):
    pages = [{"id": "S-01", "url": "https://example.com/a", "expect": "ok"}]
    save_pages.run(
        pages, fetch=lambda url: FetchOk("a   b\n c", "web"), out_dir=tmp_path
    )
    assert (tmp_path / "S-01.txt").read_text(encoding="utf-8") == save.normalise_text(
        "a   b\n c"
    )
    assert (tmp_path / "S-01.txt").read_text(encoding="utf-8") == "a b c"


def test_failed_fetch_writes_no_file_and_continues(tmp_path, capsys):
    pages = [
        {"id": "S-01", "url": "https://example.com/a", "expect": "ok"},
        {"id": "S-02", "url": "https://example.com/b", "expect": "ok"},
    ]

    def fake(url):
        return FetchFail("boom") if url.endswith("/a") else FetchOk("text here", "web")

    save_pages.run(pages, fetch=fake, out_dir=tmp_path)
    assert not (tmp_path / "S-01.txt").exists()
    assert (tmp_path / "S-02.txt").exists()
    out = capsys.readouterr().out
    assert "S-01" in out
    assert "boom" in out


def test_pages_json_ids_and_urls():
    assert [p["id"] for p in PAGES] == [f"S-{n:02d}" for n in range(1, 16)]
    for p in PAGES:
        assert p["url"].startswith("https://")
        assert p["expect"] in ("ok", "unreadable")


def test_golden_files_within_limits():
    urls = {p["id"]: p["url"] for p in PAGES}
    for path in GOLDEN.glob("*.txt"):
        host = urlsplit(urls[path.stem]).hostname
        floor = (
            config.MIN_TEXT_CHARS_GITHUB
            if host == "github.com"
            else config.MIN_TEXT_CHARS_HTML
        )
        n = len(path.read_text(encoding="utf-8"))
        assert floor <= n <= config.MAX_PAGE_CHARS, path.name


def test_expect_ok_has_file_and_s15_has_none():
    for p in PAGES:
        if p["expect"] == "ok":
            assert (GOLDEN / f"{p['id']}.txt").exists(), p["id"]
    s15 = next(p for p in PAGES if p["id"] == "S-15")
    assert s15["expect"] == "unreadable"
    assert not (GOLDEN / "S-15.txt").exists()
