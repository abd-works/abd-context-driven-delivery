"""Scanner: CE `//` comments are invariants and sequencing notes only.

Descriptive prose, implementation asides, and cross-references in `//`
comments are a defect. Keep comments to must/never/always/before/after notes.
"""
from __future__ import annotations

import re
from pathlib import Path

from scanners import Scanner

RULE = "ce-comments-are-for-invariants-and-sequencing-notes-only"

_COMMENT = re.compile(r"(?:^|\s)//\s*(.+)$")
_INVARIANT_OR_SEQUENCE = re.compile(
    r"\b(must|never|always|only|before|after|then|once|when)\b",
    re.IGNORECASE,
)
_PROSE = re.compile(
    r"(?:—|--|⚠️|transient|value object|carries|same concept|"
    r"implementation|see also|cross-ref|split namespace)",
    re.IGNORECASE,
)
_SKIP_PARTS = frozenset({"templates", "examples", "evals"})


class CeCommentsAreForInvariantsScanner(Scanner):
    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if file_path.suffix.lower() not in {".md", ".txt"}:
            return []
        if any(part in _SKIP_PARTS for part in file_path.parts):
            return []
        try:
            text = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []
        violations = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            match = _COMMENT.search(line)
            if match is None:
                continue
            body = match.group(1).strip()
            if not body:
                continue
            if _INVARIANT_OR_SEQUENCE.search(body) and not _PROSE.search(body):
                continue
            if _PROSE.search(body) or not _INVARIANT_OR_SEQUENCE.search(body):
                violations.append(
                    self.violation(
                        "CE // comment is descriptive prose. Use // only for "
                        "invariants and sequencing notes "
                        f"(must/never/before/after): {body[:80]!r}",
                        location=str(file_path),
                        line=lineno,
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
            CeCommentsAreForInvariantsScanner, RULE, collect_markdown_files
        )
    )
