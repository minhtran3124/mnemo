from pathlib import Path

import pytest
from pydantic import ValidationError

import config

FAKE_KEY = "sk-ant-fake-key-for-tests"


def make_settings(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    return config.Settings(_env_file=None)


def test_constants():
    assert config.MODEL == "claude-haiku-5-5"
    assert config.MAX_TOKENS == 1024
    assert config.MAX_PAGE_CHARS == 20_000


def test_no_temperature_default():
    assert not hasattr(config, "TEMPERATURE")


def test_key_hidden_in_str_and_repr(monkeypatch):
    settings = make_settings(monkeypatch)
    assert FAKE_KEY not in str(settings)
    assert FAKE_KEY not in repr(settings)


def test_secret_value_readable(monkeypatch):
    settings = make_settings(monkeypatch)
    assert settings.api_key.get_secret_value() == FAKE_KEY


def test_missing_key_raises_clear_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValidationError, match="ANTHROPIC_API_KEY"):
        config.Settings(_env_file=None)


def test_env_file_independent_of_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    env_file = Path(config.Settings.model_config["env_file"])
    assert env_file.is_absolute()
    assert env_file == Path(config.__file__).resolve().parent / ".env"


def test_api_notes_checked_rows_cite_a_url_and_intro_allows_them():
    text = (Path(config.__file__).parent / "docs/reference/api-notes.md").read_text()
    assert "Nothing here is a verified fact" not in text
    assert "**Checked**" in text.split("| # |")[0]
    rows = [line for line in text.splitlines() if "| Checked |" in line]
    assert rows
    for row in rows:
        assert "https://" in row
