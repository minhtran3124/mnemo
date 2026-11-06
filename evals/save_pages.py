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
) -> None:
    """Fetch every page and write the normalised text of each one that loads.

    A failed fetch prints its id, URL and reason and writes nothing; any
    existing golden file is left as it is.
    """
    for page in pages:
        result = fetch(page["url"])
        if isinstance(result, fetcher.FetchOk):
            out_dir.mkdir(parents=True, exist_ok=True)
            text = save.normalise_text(result.text)
            (out_dir / f"{page['id']}.txt").write_text(text, encoding="utf-8")
        else:
            print(f"{page['id']} {page['url']}: {result.reason}")


def main() -> int:
    """Save every golden page that can be fetched."""
    pages = json.loads(PAGES_FILE.read_text(encoding="utf-8"))
    run(pages)
    return 0


if __name__ == "__main__":
    sys.exit(main())
