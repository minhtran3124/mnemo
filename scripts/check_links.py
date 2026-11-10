"""Check that every relative link in the markdown files points at a real file.

Run from anywhere: `uv run python scripts/check_links.py`. It reads files only,
calls no network and no model. Web links and `#anchor` links are skipped.

Exit codes: 0 no broken link, 1 at least one broken link.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {
    "node_modules",
    ".venv",
    "specs",
    ".git",
    ".pytest_cache",
    ".playwright-mcp",
}
SKIP_PREFIXES = (".claude/skills/",)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
EXTERNAL = re.compile(r"^([a-z][a-z0-9+.-]*:|#)", re.IGNORECASE)


def markdown_files() -> list[Path]:
    found = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT)
        if SKIP_PARTS & set(rel.parts) or rel.as_posix().startswith(SKIP_PREFIXES):
            continue
        found.append(path)
    return found


def broken_links(path: Path) -> tuple[int, list[str]]:
    checked = 0
    broken = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        for match in LINK.finditer(line):
            target = match.group(1)
            if EXTERNAL.match(target):
                continue
            checked += 1
            file_part = target.split("#")[0]
            if file_part and not (path.parent / file_part).exists():
                broken.append(f"{path.relative_to(ROOT)}:{number}: {target}")
    return checked, broken


def main() -> int:
    total = 0
    problems: list[str] = []
    for path in markdown_files():
        checked, broken = broken_links(path)
        total += checked
        problems.extend(broken)
    for problem in problems:
        print(problem)
    print(f"checked {total} relative links, {len(problems)} broken")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
