"""Model grader: does the page text support every statement in a summary?

Sonnet 5.5 reads the page text, the summary and the key facts. It lists the
summary statements the page does not support and answers each key fact yes or
no. Invalid output is retried once, then the page is marked `grader_failed` and
not scored. A transient API error (timeout, connection, 429, 5xx) that the SDK
already retried also marks the page `grader_failed`, so one bad call does not abort
the run. A missing key or an auth error propagates (not a page problem).
"""

from dataclasses import dataclass, field
from pathlib import Path

import anthropic
from pydantic import BaseModel, ValidationError

import client
import config

PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "eval_faithful.txt"
ATTEMPTS = 2


def _is_transient(error: Exception) -> bool:
    """True for errors that say nothing about the page: timeout, network, 429, 5xx."""
    if isinstance(error, anthropic.APITimeoutError | anthropic.APIConnectionError):
        return True
    return isinstance(error, anthropic.APIStatusError) and (
        error.status_code == 429 or error.status_code >= 500
    )


class FaithfulOutput(BaseModel):
    """What the grader returns for one summary."""

    unsupported: list[str]
    key_fact_results: list[bool]


@dataclass(frozen=True)
class FaithfulResult:
    passed: bool
    unsupported_count: int | None
    unsupported: list[str] = field(default_factory=list)
    key_facts: list[bool] = field(default_factory=list)
    usage: client.Usage = field(default_factory=lambda: client.Usage(0, 0))
    grader_failed: bool = False


def _message(page_text: str, summary: str, key_facts: list[str]) -> str:
    page = " ".join(page_text.split())[: config.MAX_PAGE_CHARS]
    facts = "\n".join(f"{i}. {fact}" for i, fact in enumerate(key_facts, start=1))
    return f"<page>{page}</page>\n<summary>{summary}</summary>\n<key_facts>\n{facts}\n</key_facts>"


def grade_faithful(
    page_text: str, summary: str, key_facts: list[str]
) -> FaithfulResult:
    """Grade one summary. Passes only with zero unsupported statements."""
    system = PROMPT_FILE.read_text(encoding="utf-8")
    messages = [{"role": "user", "content": _message(page_text, summary, key_facts)}]
    input_tokens = output_tokens = 0
    for _ in range(ATTEMPTS):
        try:
            out, usage = client.parse_with_usage(
                messages, FaithfulOutput, system=system, model=config.EVAL_GRADER_MODEL
            )
        except (client.InvalidOutput, ValidationError):
            continue
        except anthropic.APIError as error:
            if not _is_transient(error):
                raise
            break
        input_tokens += usage.input_tokens
        output_tokens += usage.output_tokens
        if len(out.key_fact_results) != len(key_facts):
            continue
        return FaithfulResult(
            passed=not out.unsupported,
            unsupported_count=len(out.unsupported),
            unsupported=out.unsupported,
            key_facts=out.key_fact_results,
            usage=client.Usage(input_tokens, output_tokens),
        )
    return FaithfulResult(
        passed=False,
        unsupported_count=None,
        usage=client.Usage(input_tokens, output_tokens),
        grader_failed=True,
    )
