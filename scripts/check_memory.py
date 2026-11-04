"""Prove Claude keeps history across two calls (phase 0 done-when, rows 1 and 2).

Call 1 tells Claude a made-up code word. Call 2 sends that history plus a
question about the word. If the second answer holds the word, history works.
This calls the real API and costs money, so CI never runs it.

Exit codes: 0 PASS, 1 FAIL, 2 the API key is missing, 3 the API call failed
(bad key, network, timeout).
"""

import sys
from pathlib import Path

# Running `python scripts/check_memory.py` puts scripts/ on the path, not the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anthropic

import client

CODE_WORD = "zephyr-lantern-4417"
TELL = f"Remember this code word: {CODE_WORD}. Reply with one short sentence."
ASK = "What was the code word I told you? Reply with the code word only."


def _api_error(err: Exception) -> int:
    # Name the error class only: a message could carry request details.
    print(f"memory check: ERROR, the API call failed ({type(err).__name__})")
    return 3


def main() -> int:
    history = [{"role": "user", "content": TELL}]
    try:
        answer1 = client.ask(history)
    except RuntimeError as err:
        if "ANTHROPIC_API_KEY" in str(err):
            print(err)
            return 2
        raise
    except anthropic.APIError as err:
        return _api_error(err)
    print(f"call 1: {answer1}")

    history2 = [
        *history,
        {"role": "assistant", "content": answer1},
        {"role": "user", "content": ASK},
    ]
    try:
        answer2 = client.ask(history2)
    except anthropic.APIError as err:
        return _api_error(err)
    print(f"call 2: {answer2}")

    if CODE_WORD.lower() in answer2.lower():
        print("memory check: PASS")
        return 0
    print("memory check: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
