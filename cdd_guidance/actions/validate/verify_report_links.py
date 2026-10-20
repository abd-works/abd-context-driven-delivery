"""Verify markdown file links in a validation report resolve to existing sources."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def verify_report(markdown_path: Path) -> list[str]:
    text = markdown_path.read_text(encoding="utf-8")
    base = markdown_path.parent.resolve()
    errors: list[str] = []
    for _label, href in _LINK.findall(text):
        href = href.strip().strip("<>")
        if href.startswith("vscode:"):
            errors.append(f"do not use vscode:// links in reports: {href[:80]}")
            continue
        if href.startswith("file:"):
            errors.append(f"do not use file:// links in reports: {href[:80]}")
            continue
        path_part, _, fragment = href.partition("#")
        line: int | None = None
        if href.startswith(("http://", "https://")):
            errors.append(f"unsupported href scheme: {href[:80]}")
            continue
        path_candidate = Path(path_part)
        if path_candidate.is_absolute():
            target = path_candidate.resolve()
        else:
            target = (base / path_part).resolve()
        if not target.is_file():
            errors.append(f"missing file: {href} -> {target}")
            continue
        if fragment.startswith("L"):
            try:
                line = int(fragment[1:])
            except ValueError:
                errors.append(f"bad #L fragment: {href}")
                continue
        if line is not None:
            line_count = len(target.read_text(encoding="utf-8").splitlines())
            if line < 1 or line > line_count:
                errors.append(f"line {line} out of range 1..{line_count}: {href}")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_report_links.py <report.md>", file=sys.stderr)
        return 2
    path = Path(argv[1]).resolve()
    errors = verify_report(path)
    if errors:
        for item in errors:
            print(item)
        print(f"FAIL: {len(errors)} link problem(s) in {path}")
        return 1
    count = len(_LINK.findall(path.read_text(encoding="utf-8")))
    print(f"OK: {count} link(s) in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
