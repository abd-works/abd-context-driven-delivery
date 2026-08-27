"""Scanner: reuse-established-notation-not-a-parallel-one

Sketch / model interaction notation is templates/clean_engineering-sketch.md's
`-> collaborator.operation` and `// …`. Inventing a parallel bold-bullet symbol
set (`- **Interaction:** …` / `- **Invariant:** …` as collaboration markers)
is a process violation.

Exempt: Language companion identity bullets tagged `<!-- L -->` (or living
under a `## Language companion` heading) — those keep `- **Invariant:**`.
Exempt: Spec-channel indented `Interaction:` / `Invariant:` without bold.
"""
from __future__ import annotations

import re
from pathlib import Path

from scan import Scanner

RULE = "reuse-established-notation-not-a-parallel-one"

_BOLD_INTERACTION = re.compile(r"\*\*Interaction:\*\*", re.IGNORECASE)
_BOLD_INVARIANT_BULLET = re.compile(
    r"^\s*[-*]\s+\*\*Invariant:\*\*", re.IGNORECASE | re.MULTILINE
)
_L_TAG = re.compile(r"<!--\s*L\s*-->", re.IGNORECASE)
_LANG_COMPANION_HEADING = re.compile(
    r"^#{1,3}\s+Language companion\b", re.IGNORECASE
)
_ANY_HEADING = re.compile(r"^#{1,6}\s+")
# Guidance that quotes the forbidden form while forbidding it.
_META_PROHIBITION = re.compile(
    r"do\s+\*\*not\*\*\s+invent|do not invent|never invent|"
    r"parallel symbol|parallel bullet|as collaboration markers|"
    r"different surfaces",
    re.IGNORECASE,
)


class ReuseEstablishedNotationScanner(Scanner):
    """Flag invented bold-bullet Interaction/Invariant forms in markdown."""

    RULE = RULE

    def scan(self, root: Path, files: list[Path]) -> list:
        # Process/markdown fixtures are often under examples/; do not drop them
        # when the caller passed explicit paths (repair / verify_regression).
        violations = []
        for file_path in files:
            path = file_path if file_path.is_absolute() else Path(root) / file_path
            if not path.is_file() or path.suffix.lower() != ".md":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            violations.extend(self._scan_text(path, text))
        return violations

    def _scan_text(self, path: Path, text: str) -> list:
        violations = []
        in_language_companion = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if _LANG_COMPANION_HEADING.match(line):
                in_language_companion = True
            elif _ANY_HEADING.match(line) and not _LANG_COMPANION_HEADING.match(line):
                in_language_companion = False

            if _META_PROHIBITION.search(line):
                continue

            if _BOLD_INTERACTION.search(line):
                violations.append(
                    self.violation(
                        "Invented bold-bullet Interaction form. "
                        "Reuse sketch notation: nest `-> {collaborator}.{operation}` "
                        "under the calling operation "
                        "(see templates/clean_engineering-sketch.md).",
                        location=str(path),
                        line=lineno,
                    )
                )
                continue

            if _BOLD_INVARIANT_BULLET.search(line):
                if in_language_companion or _L_TAG.search(line):
                    continue
                violations.append(
                    self.violation(
                        "Bold-bullet Invariant used as sketch/model collaboration "
                        "notation. Reuse `// …` nested under the operation or on "
                        "the class (Language companion `- **Invariant:**` with "
                        "<!-- L --> is a different surface).",
                        location=str(path),
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
    from scan import run_scanner_main

    raise SystemExit(
        run_scanner_main(
            ReuseEstablishedNotationScanner,
            RULE,
            collect_markdown_files,
        )
    )
