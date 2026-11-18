"""Tunable values for Mnemo, in one place (NF-02).

The model name and the size limits live here and nowhere else. The API key is
read from the environment or a gitignored `.env` and is never printed.
"""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Haiku 5.5 for mnemo/save/pipeline.py (D-022). Name checked on the official models page.
MODEL = "claude-haiku-5-5"

# Sonnet 5.5 grades summaries in the eval harness. The grader is stronger than
# the writer (MODEL), so it can catch what the writer got wrong. Name checked on
# the official models page.
EVAL_GRADER_MODEL = "claude-sonnet-5-5"

# Output cap per call. A summary, title and folder fit well under this, and a
# low cap bounds the cost of one call (NF-02).
MAX_TOKENS = 1024

# Page text cap in characters, checked before the call. About 5k tokens of
# input: enough for the start of an article, small enough to keep each save
# cheap (NF-02).
MAX_PAGE_CHARS = 20_000

# The only folders a bookmark may be filed in (D-005, FO-01 to FO-04).
# Unsorted is the null folder: it always exists and cannot be deleted.
STARTER_FOLDERS = ("Work", "Learning", "Reference", "Personal", "Ideas")
UNSORTED = "Unsorted"


def is_allowed_folder(name: object) -> bool:
    """True for one starter folder or Unsorted, with exact letter case."""
    return isinstance(name, str) and (name in STARTER_FOLDERS or name == UNSORTED)


# The save prompt version used by default (phase 3). The eval overrides it per
# run with `--prompt-version`. Keep this on the best compared version.
SAVE_PROMPT_VERSION = "save_v5"

# Ask tools (phase 4): the most results one keyword search returns.
SEARCH_RESULT_LIMIT = 10

# Ask loop (phase 4): stop a tool loop that never ends.
ASK_MAX_ROUNDS = 6

# Import preview (phase 4, IM-04): the estimate is new links times this token
# figure times the price per million tokens, all in US dollars.
# Unverified: the per-link token figure and the current Claude API prices. Check
# both against the official pricing page before relying on the estimate.
IMPORT_TOKENS_PER_LINK = 2_000
IMPORT_PRICE_PER_MILLION_TOKENS = 3.0

# Ask answer (phase 4): at most this many bookmarks in one reply (AA-02).
ASK_ANSWER_LIMIT = 3

# Fetch limits (page-reading.md, "Fetch limits"). Starting values, tune in phase 1.
FETCH_CONNECT_TIMEOUT = 5.0
FETCH_READ_TIMEOUT = 10.0
FETCH_WRITE_TIMEOUT = 5.0
FETCH_POOL_TIMEOUT = 5.0
# httpx has no total timeout, so the read loop checks this per attempt.
FETCH_ATTEMPT_SECONDS = 15.0
# One retry for a transient error, after this many seconds (PR-03).
FETCH_RETRY_DELAY = 1.0
# Decoded bytes. Refuse early on Content-Length, stop reading at the cap.
FETCH_MAX_BYTES = 2_000_000
FETCH_CONTENT_TYPES = ("text/html", "application/xhtml+xml", "text/plain")
FETCH_MAX_REDIRECTS = 5
FETCH_ALLOWED_PORTS = (80, 443)
FETCH_MAX_URL_CHARS = 2048
# Seconds allowed for the DNS lookup, so a stalling resolver cannot hold a
# save open (NF-02).
FETCH_DNS_TIMEOUT = 5.0

# Minimum text after whitespace is collapsed (PR-04). The fetcher only exposes
# these; mnemo/save/pipeline.py decides when text is too short.
MIN_TEXT_CHARS_HTML = 300
MIN_TEXT_CHARS_GITHUB = 40
# Pasted text skips the fetch but uses the same low floor, so a one-character
# paste never gets an invented summary.
MIN_TEXT_CHARS_PASTED = 40

USER_AGENT = "Mnemo/0.1 (personal bookmark app)"
GITHUB_API_BASE = "https://api.github.com"

# The repo root holds .env and data/, so the key is found from any working directory.
ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"

# No sampling settings are sent: current models do not take them (tech-stack.md).


class Settings(BaseSettings):
    """Secrets read from the environment. Build it only where the key is needed."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    api_key: SecretStr = Field(alias="ANTHROPIC_API_KEY")


class GithubSettings(BaseSettings):
    """Optional GitHub token. Kept apart so a missing Anthropic key never blocks it."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    github_token: SecretStr | None = Field(default=None, alias="GITHUB_TOKEN")


def get_github_token() -> str | None:
    """The optional GITHUB_TOKEN, or None. Send it only to GITHUB_API_BASE."""
    token = GithubSettings().github_token
    value = token.get_secret_value().strip() if token else ""
    return value or None


def get_settings() -> Settings:
    """Load settings. Raises a validation error naming ANTHROPIC_API_KEY if unset."""
    return Settings()  # type: ignore[call-arg]
