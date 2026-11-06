"""Save the normalised text of the golden pages to evals/golden/.

Run once from the repo root: uv run python -m evals.save_pages
"""

import json
import sys
from collections.abc import Callable
from pathlib import Path

import fetcher
import save

EVALS_DIR = Path(__file__).parent
PAGES_FILE = EVALS_DIR / "pages.json"
GOLDEN_DIR = EVALS_DIR / "golden"


def run(
    pages: list[dict],
    fetch: Callable[[str], fetcher.FetchResult] = fetcher.fetch,
    out_dir: Path = GOLDEN_DIR,
) -> list[str]:
    """Fetch every page and write the text of those expected to be readable.

    Pages marked "unreadable" are fetched too but get no golden file. A failed
    fetch prints its reason; for an expect-ok page it also removes any older
    golden file and counts as failed. A readable page marked "unreadable" is
    reported so the entry can be flipped. Return the ids that failed.
    """
    failed: list[str] = []
    for page in pages:
        expect_ok = page["expect"] == "ok"
        result = fetch(page["url"])
        if isinstance(result, fetcher.FetchOk):
            if expect_ok:
                out_dir.mkdir(parents=True, exist_ok=True)
                text = save.normalise_text(result.text)
                (out_dir / f"{page['id']}.txt").write_text(text, encoding="utf-8")
            else:
                print(f"{page['id']} {page['url']}: now readable, expect is unreadable")
        else:
            print(f"{page['id']} {page['url']}: {result.reason}")
            if expect_ok:
                (out_dir / f"{page['id']}.txt").unlink(missing_ok=True)
                failed.append(page["id"])
    return failed


def main() -> int:
    """Save every golden page. Return 1 if any page failed, else 0."""
    pages = json.loads(PAGES_FILE.read_text(encoding="utf-8"))
    failed = run(pages)
    print(f"failed: {', '.join(failed) if failed else 'none'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
