"""Save the normalised text of the golden pages to evals/golden/.

Run once from the repo root: uv run python -m evals.save_pages
"""

import json
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
    """Fetch every page expected to be readable and write its text.

    Pages marked "unreadable" are skipped: they get no golden file and a
    failed fetch is not reported for them. Return the ids that failed.
    """
    failed: list[str] = []
    for page in pages:
        if page["expect"] != "ok":
            continue
        result = fetch(page["url"])
        if isinstance(result, fetcher.FetchOk):
            out_dir.mkdir(parents=True, exist_ok=True)
            text = save.normalise_text(result.text)
            (out_dir / f"{page['id']}.txt").write_text(text, encoding="utf-8")
        else:
            print(f"{page['id']} {page['url']}: {result.reason}")
            failed.append(page["id"])
    return failed


def main() -> None:
    pages = json.loads(PAGES_FILE.read_text(encoding="utf-8"))
    failed = run(pages)
    print(f"failed: {', '.join(failed) if failed else 'none'}")


if __name__ == "__main__":
    main()
