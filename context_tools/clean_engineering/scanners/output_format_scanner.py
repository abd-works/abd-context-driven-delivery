"""Scanner: `output-format` — generated markdown has no template markup.

Internal toolset comments such as `<!-- Mu -->` must never appear in written
output. Module headings must sit immediately above their purpose block — no
blank line between `# name` and `- **Purpose:**`.
"""
from __future__ import annotations

import re
from pathlib import Path

from scanners import Scanner

RULE = "output-format"

_TOOLSET_COMMENT = re.compile(r"<!--\s*[A-Za-z]{1,3}\s*-->")
_HEADING = re.compile(r"^#{1,6}\s+\S")
_PURPOSE_BULLET = re.compile(r"^-\s+\*\*")
_SKIP_PARTS = frozenset({"templates", "examples", "evals"})


class OutputFormatScanner(Scanner):
    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if file_path.suffix.lower() != ".md":
            return []
        if any(part in _SKIP_PARTS for part in file_path.parts):
            return []
        try:
            text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []
        violations = []
        lines = text.splitlines()
        for lineno, line in enumerate(lines, start=1):
            if _TOOLSET_COMMENT.search(line):
                violations.append(
                    self.violation(
                        "Template annotation comment leaked into output. "
                        "Strip <!-- Mu --> / <!-- Mv --> and similar markup "
                        "before writing the file.",
                        location=str(file_path),
                        line=lineno,
                    )
                )
        for index, line in enumerate(lines[:-2]):
            if not _HEADING.match(line):
                continue
            if lines[index + 1].strip() != "":
                continue
            if _PURPOSE_BULLET.match(lines[index + 2]):
                violations.append(
                    self.violation(
                        "Blank line between heading and its purpose block. "
                        "Write '# name' immediately followed by '- **Purpose:**'.",
                        location=str(file_path),
                        line=index + 2,
                    )
                )
        return violations


def collect_markdown_files(root: Path) -> list[Path]:
    root = root.resolve()
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.is_file() and not Scanner.is_skipped_path(path)
    )


if __name__ == "__main__":
    from scanners.scanner_runner import ScannerRunner

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            OutputFormatScanner, RULE, collect_markdown_files
        )
    )
