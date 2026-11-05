import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

WEB = Path(__file__).resolve().parent.parent / "web"
FONTS = ["Newsreader", "PublicSans", "SplineSansMono"]
TOKENS = [
    "bg",
    "surface",
    "ink",
    "ink2",
    "muted",
    "line-strong",
    "rule",
    "ctl-line",
    "accent",
    "accent-hover",
    "on-accent",
    "warn-bg",
    "warn",
    "warn-text",
]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake-key-for-tests")
    import server

    return TestClient(server.app)


def css_files() -> list[Path]:
    return sorted(WEB.rglob("*.css"))


def test_fonts_are_served_from_static(client):
    for name in FONTS:
        response = client.get(f"/static/fonts/{name}.woff2")
        assert response.status_code == 200, name
        assert response.content[:4] == b"wOF2", name


def test_each_font_has_a_licence_file():
    for name in FONTS:
        licence = WEB / "fonts" / f"{name}-OFL.txt"
        assert licence.is_file(), name
        assert "SIL OPEN FONT LICENSE" in licence.read_text(encoding="utf-8").upper()


def test_no_css_loads_anything_from_the_network():
    assert css_files()
    for path in css_files():
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"https?://", text), path.name
        assert not re.search(r"@import", text), path.name


def test_tokens_defined_for_light_system_dark_and_explicit_dark():
    text = (WEB / "css" / "tokens.css").read_text(encoding="utf-8")
    light, dark_media, dark_attr = re.search(
        r"^:root\s*\{(.*?)\}"
        r".*?prefers-color-scheme:\s*dark\)\s*\{\s*"
        r":root:not\(\[data-theme=\"light\"\]\)\s*\{(.*?)\}\s*\}"
        r".*?:root\[data-theme=\"dark\"\]\s*\{(.*?)\}",
        text,
        re.DOTALL | re.MULTILINE,
    ).groups()
    for block in (light, dark_media, dark_attr):
        for token in TOKENS:
            assert re.search(rf"--{re.escape(token)}\s*:", block), token
        assert "color-scheme" in block


def test_hex_colours_only_in_tokens_css():
    assert css_files()
    for path in css_files():
        if path.name == "tokens.css":
            continue
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b", text), path.name


def test_shared_header_has_system_light_and_dark_choices():
    header = (WEB / "partials" / "header.html").read_text(encoding="utf-8")
    assert "<header" in header
    for choice in ("system", "light", "dark"):
        assert f'data-theme-choice="{choice}"' in header
    for label in ("System", "Light", "Dark"):
        assert f">{label}<" in header or f"{label}</span>" in header
    assert 'href="/settings"' in header


def test_settings_page_has_appearance_radios_and_remember_line(client):
    response = client.get("/settings")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    body = response.text
    assert "Appearance" in body
    assert len(re.findall(r'type="radio"', body)) == 3
    assert "Mnemo remembers your choice on this device." in body
    assert "<header" in body
