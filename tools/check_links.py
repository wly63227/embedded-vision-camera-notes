"""Check relative Markdown file links without third-party dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    failures: list[str] = []
    for markdown in ROOT.rglob("*.md"):
        if ".git" in markdown.parts or "build" in markdown.parts:
            continue
        text = markdown.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            target = target.strip().split(maxsplit=1)[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = unquote(target.split("#", 1)[0])
            if not path_part:
                continue
            resolved = (markdown.parent / path_part).resolve()
            if not resolved.exists():
                failures.append(f"{markdown.relative_to(ROOT)} -> {target}")

    if failures:
        print("Broken internal links:")
        print("\n".join(f"- {item}" for item in failures))
        return 1
    print("All internal Markdown file links are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

