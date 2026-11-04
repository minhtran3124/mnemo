"""Tunable values for Mnemo, in one place (NF-02).

The model name and the size limits live here and nowhere else. The API key is
read from the environment or a gitignored `.env` and is never printed.
"""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Haiku 5.5 for save.py (D-022). Name checked on the official models page.
MODEL = "claude-haiku-5-5"

# Output cap per call. A summary, title and folder fit well under this, and a
# low cap bounds the cost of one call (NF-02).
MAX_TOKENS = 1024

# Page text cap in characters, checked before the call. About 5k tokens of
# input: enough for the start of an article, small enough to keep each save
# cheap (NF-02).
MAX_PAGE_CHARS = 20_000

# The .env sits next to this file, so the key is found from any working directory.
ENV_FILE = Path(__file__).resolve().parent / ".env"

# No default temperature: not confirmed for current models (tech-stack.md).


class Settings(BaseSettings):
    """Secrets read from the environment. Build it only where the key is needed."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    api_key: SecretStr = Field(alias="ANTHROPIC_API_KEY")


def get_settings() -> Settings:
    """Load settings. Raises a validation error naming ANTHROPIC_API_KEY if unset."""
    return Settings()  # type: ignore[call-arg]
