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


def rule_body(css: str, selector: str) -> str:
    """Body of the rule whose selector is exactly `selector` (not a list)."""
    match = re.search(rf"^{re.escape(selector)}\s*\{{([^}}]*)\}}", css, re.MULTILINE)
    assert match, f"no standalone `{selector}` rule found in base.css"
    return match.group(1)


def token_blocks(text: str) -> tuple[str, str, str]:
    """Light, system-dark and explicit-dark token blocks of tokens.css."""
    pattern = (
        r"^:root\s*\{(.*?)\}"
        r".*?prefers-color-scheme:\s*dark\)\s*\{\s*"
        r":root:not\(\[data-theme=\"light\"\]\)\s*\{(.*?)\}\s*\}"
        r".*?:root\[data-theme=\"dark\"\]\s*\{(.*?)\}"
    )
    match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
    assert match, (
        "tokens.css must define :root, the system-dark media block and :root[data-theme=dark]"
    )
    return match.group(1), match.group(2), match.group(3)


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
    light, dark_media, dark_attr = token_blocks(text)
    for block in (light, dark_media, dark_attr):
        for token in TOKENS:
            assert re.search(rf"--{re.escape(token)}\s*:", block), token
        assert "color-scheme" in block


def test_system_dark_and_explicit_dark_hold_identical_values():
    text = (WEB / "css" / "tokens.css").read_text(encoding="utf-8")
    _, dark_media, dark_attr = token_blocks(text)

    def declarations(block):
        return dict(re.findall(r"(-{0,2}[\w-]+)\s*:\s*([^;]+?)\s*;", block))

    assert "color-scheme" in declarations(dark_media)
    assert declarations(dark_media) == declarations(dark_attr)


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


def test_theme_control_does_not_clip_the_focus_ring():
    css = (WEB / "css" / "base.css").read_text(encoding="utf-8")
    block = rule_body(css, ".theme-control")
    assert "overflow" not in block


def test_focused_theme_button_paints_above_its_siblings():
    css = (WEB / "css" / "base.css").read_text(encoding="utf-8")
    block = rule_body(css, ".theme-btn:focus-visible")
    assert re.search(r"position:\s*relative", block)
    assert re.search(r"z-index:\s*1\s*;", block)


def test_site_nav_wraps_on_narrow_phones():
    css = (WEB / "css" / "base.css").read_text(encoding="utf-8")
    block = rule_body(css, ".site-nav")
    assert re.search(r"flex-wrap:\s*wrap", block)


@pytest.mark.parametrize(
    "path", ["/static/settings.html", "/static/partials/header.html"]
)
def test_unrendered_pages_and_partials_are_not_served(client, path):
    assert client.get(path).status_code == 404


def test_css_and_js_are_still_served_from_static(client):
    assert client.get("/static/css/tokens.css").status_code == 200
    assert client.get("/static/js/theme.js").status_code == 200
