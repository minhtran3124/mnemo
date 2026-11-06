"""The only module that builds the Anthropic client (F-chat/save helpers).

Callers cap input size (config.MAX_PAGE_CHARS); ask() does no input check and
enforces the output cap with config.MAX_TOKENS. The key is read through
config.get_settings() and never logged or put in an error.
"""

import logging
import time
from typing import NamedTuple

import anthropic
from pydantic import BaseModel, ValidationError

import config

# Every call has a timeout. The SDK retries only safe errors, with backoff.
TIMEOUT_SECONDS = 30.0
MAX_RETRIES = 2

_log = logging.getLogger("mnemo.client")


class InvalidOutput(RuntimeError):
    """Claude refused, hit max_tokens or gave no parsed output. Callers retry or fall back."""


_client: anthropic.Anthropic | None = None


class MissingKey(RuntimeError):
    """The API key is missing or empty (a config error, never a page problem)."""


def _get_client() -> anthropic.Anthropic:
    """Build the client on first use, so importing this module needs no key."""
    global _client
    if _client is None:
        try:
            settings = config.get_settings()
        except ValidationError:
            raise MissingKey(
                "ANTHROPIC_API_KEY is missing or empty; set it in the environment or .env"
            ) from None
        api_key = settings.api_key.get_secret_value()
        if not api_key.strip():
            # Settings accepts an empty string, so check it here.
            raise MissingKey(
                "ANTHROPIC_API_KEY is missing or empty; set it in the environment or .env"
            )
        _client = anthropic.Anthropic(
            api_key=api_key,
            timeout=TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES,
        )
    return _client


def ask(
    messages: list[dict],
    system: str | None = None,
    stop_sequences: list[str] | None = None,
) -> str:
    """Send messages to Claude and return the concatenated text of the reply."""
    kwargs: dict = {
        "model": config.MODEL,
        "max_tokens": config.MAX_TOKENS,
        "messages": messages,
    }
    if system is not None:
        kwargs["system"] = system
    if stop_sequences is not None:
        kwargs["stop_sequences"] = stop_sequences

    sdk = _get_client()
    start = time.perf_counter()
    response = sdk.messages.create(**kwargs)
    latency_ms = round((time.perf_counter() - start) * 1000)

    _log.info(
        "claude call model=%s input_tokens=%s output_tokens=%s latency_ms=%s",
        config.MODEL,
        response.usage.input_tokens,
        response.usage.output_tokens,
        latency_ms,
    )

    if response.stop_reason == "max_tokens":
        # The reply hit the output cap. Return what came back; the log tells callers why it is short.
        _log.warning("claude reply stopped at max_tokens=%s", config.MAX_TOKENS)

    text = "".join(b.text for b in response.content if b.type == "text")
    if not text:
        raise RuntimeError("Claude returned no text")
    return text


class Usage(NamedTuple):
    """Token counts for one call. Tokens only, no money."""

    input_tokens: int
    output_tokens: int


def parse_with_usage[T: BaseModel](
    messages: list[dict],
    output_format: type[T],
    system: str | None = None,
    model: str | None = None,
) -> tuple[T, Usage]:
    """Like parse(), but also return the token counts. model=None means config.MODEL.

    Sends no prefill, no stop sequence, no beta header and no sampling settings. A refusal
    or a reply cut off at max_tokens raises InvalidOutput (a RuntimeError).
    """
    model = model or config.MODEL
    kwargs: dict = {
        "model": model,
        "max_tokens": config.MAX_TOKENS,
        "messages": messages,
        "output_format": output_format,
    }
    if system is not None:
        kwargs["system"] = system

    sdk = _get_client()
    start = time.perf_counter()
    response = sdk.messages.parse(**kwargs)
    latency_ms = round((time.perf_counter() - start) * 1000)

    _log.info(
        "claude call model=%s input_tokens=%s output_tokens=%s latency_ms=%s",
        model,
        response.usage.input_tokens,
        response.usage.output_tokens,
        latency_ms,
    )

    if response.stop_reason == "refusal":
        raise InvalidOutput("Claude refused the request; treat the output as invalid")
    if response.stop_reason == "max_tokens":
        raise InvalidOutput(
            f"Claude reply hit max_tokens={config.MAX_TOKENS}; treat the output as invalid"
        )
    if response.parsed_output is None:
        raise InvalidOutput("Claude returned no parsed output")
    usage = Usage(response.usage.input_tokens, response.usage.output_tokens)
    return response.parsed_output, usage


def parse[T: BaseModel](
    messages: list[dict],
    output_format: type[T],
    system: str | None = None,
) -> T:
    """Send messages to Claude and return the reply as a validated output_format object.

    Sends no prefill, no stop sequence and no beta header. A refusal or a reply cut
    off at max_tokens raises InvalidOutput (a RuntimeError); callers treat that as invalid output.
    """
    parsed, _ = parse_with_usage(messages, output_format, system)
    return parsed
